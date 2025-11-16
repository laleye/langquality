"""Dashboard generator."""

from pathlib import Path
from typing import List
import plotly.graph_objects as go
import plotly.express as px
from jinja2 import Template

from ..pipeline.results import AnalysisResults
from ..recommendations.models import Recommendation


class DashboardGenerator:
    """Generates interactive HTML dashboard."""
    
    def __init__(self):
        """Initialize the dashboard generator."""
        self.template_path = Path(__file__).parent / "templates" / "dashboard.html"
    
    def _create_length_distribution_chart(self, structural_metrics) -> str:
        """Create histogram chart for sentence length distribution.
        
        Args:
            structural_metrics: StructuralMetrics object
            
        Returns:
            HTML string containing the Plotly chart
        """
        if not structural_metrics or not structural_metrics.length_histogram:
            return "<p>Aucune donnée disponible pour la distribution de longueur.</p>"
        
        # Extract data from histogram
        word_counts = sorted(structural_metrics.length_histogram.keys())
        frequencies = [structural_metrics.length_histogram[wc] for wc in word_counts]
        
        # Create histogram
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=word_counts,
            y=frequencies,
            marker_color='rgb(102, 126, 234)',
            name='Fréquence',
            hovertemplate='<b>%{x} mots</b><br>Fréquence: %{y}<extra></extra>'
        ))
        
        # Add vertical lines for thresholds if available
        word_dist = structural_metrics.word_distribution
        if word_dist:
            mean_val = word_dist.get('mean', 0)
            fig.add_vline(
                x=mean_val, 
                line_dash="dash", 
                line_color="green",
                annotation_text=f"Moyenne: {mean_val:.1f}",
                annotation_position="top"
            )
        
        fig.update_layout(
            title="Distribution de la longueur des phrases (en mots)",
            xaxis_title="Nombre de mots",
            yaxis_title="Nombre de phrases",
            hovermode='x',
            template='plotly_white',
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id="length_distribution_chart")
    
    def _create_domain_pie_chart(self, domain_metrics) -> str:
        """Create pie chart for domain distribution.
        
        Args:
            domain_metrics: DomainMetrics object
            
        Returns:
            HTML string containing the Plotly chart
        """
        if not domain_metrics or not domain_metrics.domain_counts:
            return "<p>Aucune donnée disponible pour la distribution des domaines.</p>"
        
        # Extract data
        domains = list(domain_metrics.domain_counts.keys())
        counts = list(domain_metrics.domain_counts.values())
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=domains,
            values=counts,
            hole=0.3,
            marker=dict(
                colors=px.colors.qualitative.Set3
            ),
            hovertemplate='<b>%{label}</b><br>Phrases: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Distribution des domaines thématiques",
            template='plotly_white',
            height=450
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id="domain_pie_chart")
    
    def _create_complexity_indicators(self, linguistic_metrics) -> str:
        """Create visual indicators for complexity metrics with color coding.
        
        Args:
            linguistic_metrics: LinguisticMetrics object
            
        Returns:
            HTML string with complexity indicators
        """
        if not linguistic_metrics:
            return "<p>Aucune donnée disponible pour la complexité linguistique.</p>"
        
        # Determine indicator status based on thresholds
        readability = linguistic_metrics.avg_readability_score
        complexity = linguistic_metrics.avg_lexical_complexity
        
        # Readability: higher is better (easier to read)
        # 60-100: good, 30-60: warning, 0-30: critical
        if readability >= 60:
            readability_class = "good"
            readability_status = "Bonne"
        elif readability >= 30:
            readability_class = "warning"
            readability_status = "Moyenne"
        else:
            readability_class = "critical"
            readability_status = "Difficile"
        
        # Lexical complexity: lower is better (simpler vocabulary)
        # 0-0.3: good, 0.3-0.6: warning, 0.6-1.0: critical
        if complexity <= 0.3:
            complexity_class = "good"
            complexity_status = "Simple"
        elif complexity <= 0.6:
            complexity_class = "warning"
            complexity_status = "Modérée"
        else:
            complexity_class = "critical"
            complexity_status = "Complexe"
        
        # Jargon detection
        jargon_count = len(linguistic_metrics.jargon_detected)
        if jargon_count == 0:
            jargon_class = "good"
            jargon_status = "Aucun"
        elif jargon_count <= 5:
            jargon_class = "warning"
            jargon_status = f"{jargon_count} détecté(s)"
        else:
            jargon_class = "critical"
            jargon_status = f"{jargon_count} détecté(s)"
        
        # Complex syntax
        complex_count = linguistic_metrics.complex_syntax_count
        if complex_count == 0:
            syntax_class = "good"
            syntax_status = "Aucune"
        elif complex_count <= 10:
            syntax_class = "warning"
            syntax_status = f"{complex_count} phrase(s)"
        else:
            syntax_class = "critical"
            syntax_status = f"{complex_count} phrase(s)"
        
        html = f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
            <div>
                <div class="metric-label">Lisibilité (Flesch)</div>
                <div class="indicator {readability_class}">
                    {readability:.1f} - {readability_status}
                </div>
            </div>
            <div>
                <div class="metric-label">Complexité lexicale</div>
                <div class="indicator {complexity_class}">
                    {complexity:.2f} - {complexity_status}
                </div>
            </div>
            <div>
                <div class="metric-label">Jargon détecté</div>
                <div class="indicator {jargon_class}">
                    {jargon_status}
                </div>
            </div>
            <div>
                <div class="metric-label">Syntaxe complexe</div>
                <div class="indicator {syntax_class}">
                    {syntax_status}
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _create_diversity_charts(self, diversity_metrics) -> str:
        """Create charts for diversity metrics (TTR, n-grams).
        
        Args:
            diversity_metrics: DiversityMetrics object
            
        Returns:
            HTML string containing diversity visualizations
        """
        if not diversity_metrics:
            return "<p>Aucune donnée disponible pour la diversité.</p>"
        
        html_parts = []
        
        # TTR indicator
        ttr = diversity_metrics.ttr
        vocab_coverage = diversity_metrics.vocabulary_coverage
        
        if ttr >= 0.6:
            ttr_class = "good"
            ttr_status = "Excellente"
        elif ttr >= 0.4:
            ttr_class = "warning"
            ttr_status = "Moyenne"
        else:
            ttr_class = "critical"
            ttr_status = "Faible"
        
        html_parts.append(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0;">
            <div>
                <div class="metric-label">Type-Token Ratio (TTR)</div>
                <div class="indicator {ttr_class}">
                    {ttr:.3f} - {ttr_status}
                </div>
                <div style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    {diversity_metrics.unique_words} mots uniques / {diversity_metrics.total_words} mots totaux
                </div>
            </div>
            <div>
                <div class="metric-label">Couverture vocabulaire</div>
                <div class="indicator {'good' if vocab_coverage >= 0.5 else 'warning' if vocab_coverage >= 0.3 else 'critical'}">
                    {vocab_coverage:.1%}
                </div>
            </div>
            <div>
                <div class="metric-label">Diversité des débuts</div>
                <div class="indicator {'good' if diversity_metrics.sentence_starter_diversity >= 0.7 else 'warning' if diversity_metrics.sentence_starter_diversity >= 0.5 else 'critical'}">
                    {diversity_metrics.sentence_starter_diversity:.1%}
                </div>
            </div>
        </div>
        """)
        
        # Top repetitive n-grams chart
        if diversity_metrics.repetitive_ngrams:
            top_ngrams = diversity_metrics.repetitive_ngrams[:10]  # Top 10
            ngram_texts = [ngram[0] for ngram in top_ngrams]
            ngram_counts = [ngram[1] for ngram in top_ngrams]
            
            fig = go.Figure(data=[go.Bar(
                y=ngram_texts,
                x=ngram_counts,
                orientation='h',
                marker_color='rgb(118, 75, 162)',
                hovertemplate='<b>%{y}</b><br>Répétitions: %{x}<extra></extra>'
            )])
            
            fig.update_layout(
                title="N-grams les plus répétitifs",
                xaxis_title="Nombre de répétitions",
                yaxis_title="N-gram",
                template='plotly_white',
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            html_parts.append(fig.to_html(full_html=False, include_plotlyjs=False, div_id="ngrams_chart"))
        
        # Near duplicates info
        if diversity_metrics.near_duplicates:
            dup_count = len(diversity_metrics.near_duplicates)
            html_parts.append(f"""
            <div class="metric-row">
                <span class="metric-label">Phrases quasi-identiques détectées</span>
                <span class="metric-value" style="color: #dc3545;">{dup_count} paire(s)</span>
            </div>
            """)
        
        return "\n".join(html_parts)
    
    def _create_recommendations_section(self, recommendations: List[Recommendation]) -> str:
        """Create HTML section for recommendations with severity indicators.
        
        Args:
            recommendations: List of Recommendation objects
            
        Returns:
            HTML string with formatted recommendations
        """
        if not recommendations:
            return """
            <div class="indicator good" style="display: block; text-align: center; padding: 30px;">
                ✓ Aucune recommandation critique. Votre dataset présente une bonne qualité globale !
            </div>
            """
        
        html_parts = []
        
        # Group recommendations by severity
        critical_recs = [r for r in recommendations if r.severity == "critical"]
        warning_recs = [r for r in recommendations if r.severity == "warning"]
        info_recs = [r for r in recommendations if r.severity == "info"]
        
        # Add summary
        html_parts.append(f"""
        <div style="display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap;">
            <div class="indicator critical" style="flex: 1; min-width: 150px; text-align: center;">
                <strong>{len(critical_recs)}</strong> Critique(s)
            </div>
            <div class="indicator warning" style="flex: 1; min-width: 150px; text-align: center;">
                <strong>{len(warning_recs)}</strong> Avertissement(s)
            </div>
            <div class="indicator good" style="flex: 1; min-width: 150px; text-align: center;">
                <strong>{len(info_recs)}</strong> Info(s)
            </div>
        </div>
        """)
        
        # Render each recommendation
        for rec in recommendations:
            # Determine severity class
            severity_class = rec.severity if rec.severity in ["critical", "warning", "info"] else "info"
            
            # Format affected items count
            affected_html = ""
            if rec.affected_items:
                affected_count = len(rec.affected_items)
                affected_html = f'<div class="affected-count">📌 {affected_count} élément(s) affecté(s)</div>'
            
            # Format suggested actions
            actions_html = ""
            if rec.suggested_actions:
                actions_list = "\n".join([f"<li>{action}</li>" for action in rec.suggested_actions])
                actions_html = f"""
                <div class="recommendation-actions">
                    <h4>Actions suggérées :</h4>
                    <ul>
                        {actions_list}
                    </ul>
                </div>
                """
            
            # Build recommendation card
            html_parts.append(f"""
            <div class="recommendation {severity_class}">
                <div class="recommendation-header">
                    <div class="recommendation-title">{rec.title}</div>
                    <div class="recommendation-severity {severity_class}">{rec.severity}</div>
                </div>
                <div class="recommendation-description">{rec.description}</div>
                {affected_html}
                {actions_html}
            </div>
            """)
        
        return "\n".join(html_parts)
    
    def _create_summary_section(self, results: AnalysisResults) -> str:
        """Create summary overview section with key metrics.
        
        Args:
            results: AnalysisResults object
            
        Returns:
            HTML string with summary cards
        """
        html_parts = []
        
        # Summary cards
        cards = []
        
        # Total sentences
        if results.structural:
            cards.append({
                'value': results.structural.total_sentences,
                'label': 'Phrases analysées'
            })
        
        # Average readability
        if results.linguistic:
            cards.append({
                'value': f"{results.linguistic.avg_readability_score:.1f}",
                'label': 'Score de lisibilité moyen'
            })
        
        # TTR
        if results.diversity:
            cards.append({
                'value': f"{results.diversity.ttr:.3f}",
                'label': 'Type-Token Ratio'
            })
        
        # Domains
        if results.domain:
            cards.append({
                'value': results.domain.total_domains,
                'label': 'Domaines thématiques'
            })
        
        # Gender ratio
        if results.gender_bias:
            ratio = results.gender_bias.gender_ratio
            if ratio == float('inf'):
                ratio_str = "∞"
            else:
                ratio_str = f"{ratio:.2f}"
            cards.append({
                'value': ratio_str,
                'label': 'Ratio F/M'
            })
        
        # Build summary grid
        cards_html = []
        for card in cards:
            cards_html.append(f"""
            <div class="summary-card">
                <h3>{card['label']}</h3>
                <div class="value">{card['value']}</div>
            </div>
            """)
        
        html_parts.append(f'<div class="summary-grid">{"".join(cards_html)}</div>')
        
        return "\n".join(html_parts)
    
    def _create_structural_section(self, structural_metrics) -> str:
        """Create structural analysis section.
        
        Args:
            structural_metrics: StructuralMetrics object
            
        Returns:
            HTML string with structural analysis content
        """
        if not structural_metrics:
            return "<p>Aucune donnée structurelle disponible.</p>"
        
        html_parts = []
        
        # Statistics
        word_dist = structural_metrics.word_distribution
        if word_dist:
            html_parts.append(f"""
            <h3>Statistiques de longueur (en mots)</h3>
            <div class="metric-row">
                <span class="metric-label">Minimum</span>
                <span class="metric-value">{word_dist.get('min', 0):.0f} mots</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Maximum</span>
                <span class="metric-value">{word_dist.get('max', 0):.0f} mots</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Moyenne</span>
                <span class="metric-value">{word_dist.get('mean', 0):.1f} mots</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Médiane</span>
                <span class="metric-value">{word_dist.get('median', 0):.1f} mots</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Écart-type</span>
                <span class="metric-value">{word_dist.get('std', 0):.2f}</span>
            </div>
            """)
        
        # Outliers
        too_short_count = len(structural_metrics.too_short)
        too_long_count = len(structural_metrics.too_long)
        
        if too_short_count > 0 or too_long_count > 0:
            html_parts.append(f"""
            <h3>Phrases hors limites</h3>
            <div class="metric-row">
                <span class="metric-label">Phrases trop courtes</span>
                <span class="metric-value" style="color: #dc3545;">{too_short_count}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Phrases trop longues</span>
                <span class="metric-value" style="color: #dc3545;">{too_long_count}</span>
            </div>
            """)
        
        # Length distribution chart
        html_parts.append("<h3>Distribution de longueur</h3>")
        html_parts.append(self._create_length_distribution_chart(structural_metrics))
        
        return "\n".join(html_parts)
    
    def _create_linguistic_section(self, linguistic_metrics) -> str:
        """Create linguistic analysis section.
        
        Args:
            linguistic_metrics: LinguisticMetrics object
            
        Returns:
            HTML string with linguistic analysis content
        """
        if not linguistic_metrics:
            return "<p>Aucune donnée linguistique disponible.</p>"
        
        html_parts = []
        
        # Complexity indicators
        html_parts.append("<h3>Indicateurs de complexité</h3>")
        html_parts.append(self._create_complexity_indicators(linguistic_metrics))
        
        # Detailed metrics
        html_parts.append(f"""
        <h3>Métriques détaillées</h3>
        <div class="metric-row">
            <span class="metric-label">Score de lisibilité moyen (Flesch)</span>
            <span class="metric-value">{linguistic_metrics.avg_readability_score:.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Complexité lexicale moyenne</span>
            <span class="metric-value">{linguistic_metrics.avg_lexical_complexity:.3f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Phrases avec syntaxe complexe</span>
            <span class="metric-value">{linguistic_metrics.complex_syntax_count}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Instances de jargon détectées</span>
            <span class="metric-value">{len(linguistic_metrics.jargon_detected)}</span>
        </div>
        """)
        
        return "\n".join(html_parts)
    
    def _create_diversity_section(self, diversity_metrics) -> str:
        """Create diversity analysis section.
        
        Args:
            diversity_metrics: DiversityMetrics object
            
        Returns:
            HTML string with diversity analysis content
        """
        if not diversity_metrics:
            return "<p>Aucune donnée de diversité disponible.</p>"
        
        html_parts = []
        
        html_parts.append("<h3>Métriques de diversité</h3>")
        html_parts.append(self._create_diversity_charts(diversity_metrics))
        
        return "\n".join(html_parts)
    
    def _create_domain_section(self, domain_metrics) -> str:
        """Create domain analysis section.
        
        Args:
            domain_metrics: DomainMetrics object
            
        Returns:
            HTML string with domain analysis content
        """
        if not domain_metrics:
            return "<p>Aucune donnée de domaine disponible.</p>"
        
        html_parts = []
        
        # Domain pie chart
        html_parts.append(self._create_domain_pie_chart(domain_metrics))
        
        # Domain balance info
        if domain_metrics.underrepresented or domain_metrics.overrepresented:
            html_parts.append("<h3>Équilibre des domaines</h3>")
            
            if domain_metrics.underrepresented:
                domains_list = ", ".join(domain_metrics.underrepresented)
                html_parts.append(f"""
                <div class="indicator warning" style="display: block; margin: 10px 0;">
                    ⚠️ Domaines sous-représentés (&lt;10%): {domains_list}
                </div>
                """)
            
            if domain_metrics.overrepresented:
                domains_list = ", ".join(domain_metrics.overrepresented)
                html_parts.append(f"""
                <div class="indicator warning" style="display: block; margin: 10px 0;">
                    ⚠️ Domaines sur-représentés (&gt;30%): {domains_list}
                </div>
                """)
        
        # Domain table
        if domain_metrics.domain_counts:
            html_parts.append("<h3>Détails par domaine</h3>")
            html_parts.append("<table>")
            html_parts.append("<thead><tr><th>Domaine</th><th>Nombre de phrases</th><th>Pourcentage</th></tr></thead>")
            html_parts.append("<tbody>")
            
            # Sort by count descending
            sorted_domains = sorted(
                domain_metrics.domain_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for domain, count in sorted_domains:
                percentage = domain_metrics.domain_percentages.get(domain, 0) * 100
                html_parts.append(f"<tr><td>{domain}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>")
            
            html_parts.append("</tbody></table>")
        
        return "\n".join(html_parts)
    
    def _create_gender_section(self, gender_metrics) -> str:
        """Create gender bias analysis section.
        
        Args:
            gender_metrics: GenderBiasMetrics object
            
        Returns:
            HTML string with gender analysis content
        """
        if not gender_metrics:
            return "<p>Aucune donnée de biais de genre disponible.</p>"
        
        html_parts = []
        
        # Gender ratio visualization
        ratio = gender_metrics.gender_ratio
        if ratio == float('inf'):
            ratio_str = "∞ (aucune mention masculine)"
            ratio_class = "critical"
        elif ratio == 0:
            ratio_str = "0 (aucune mention féminine)"
            ratio_class = "critical"
        elif 0.4 <= ratio <= 0.6:
            ratio_str = f"{ratio:.2f}"
            ratio_class = "good"
        else:
            ratio_str = f"{ratio:.2f}"
            ratio_class = "warning"
        
        html_parts.append(f"""
        <h3>Ratio de genre</h3>
        <div class="metric-row">
            <span class="metric-label">Mentions masculines</span>
            <span class="metric-value">{gender_metrics.masculine_count}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Mentions féminines</span>
            <span class="metric-value">{gender_metrics.feminine_count}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Ratio F/M</span>
            <span class="metric-value">
                <span class="indicator {ratio_class}">{ratio_str}</span>
            </span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Score de biais global</span>
            <span class="metric-value">
                <span class="indicator {'good' if gender_metrics.bias_score < 0.3 else 'warning' if gender_metrics.bias_score < 0.6 else 'critical'}">
                    {gender_metrics.bias_score:.2f}
                </span>
            </span>
        </div>
        """)
        
        # Stereotypes detected
        if gender_metrics.stereotypes_detected:
            html_parts.append(f"""
            <h3>Stéréotypes détectés</h3>
            <div class="indicator critical" style="display: block; margin: 10px 0;">
                ⚠️ {len(gender_metrics.stereotypes_detected)} stéréotype(s) de genre détecté(s)
            </div>
            """)
        else:
            html_parts.append("""
            <h3>Stéréotypes détectés</h3>
            <div class="indicator good" style="display: block; margin: 10px 0;">
                ✓ Aucun stéréotype de genre détecté
            </div>
            """)
        
        return "\n".join(html_parts)
    
    def generate(self, results: AnalysisResults, recommendations: List[Recommendation]) -> str:
        """Generate complete HTML dashboard from analysis results.
        
        Combines all sections into a final interactive HTML dashboard with
        charts, metrics, and recommendations.
        
        Args:
            results: AnalysisResults object containing all analysis metrics
            recommendations: List of Recommendation objects
            
        Returns:
            Complete HTML string for the dashboard
        """
        # Load template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create template
        template = Template(template_content)
        
        # Generate all sections
        timestamp = results.timestamp.strftime("%d/%m/%Y %H:%M:%S")
        summary_content = self._create_summary_section(results)
        structural_content = self._create_structural_section(results.structural)
        linguistic_content = self._create_linguistic_section(results.linguistic)
        diversity_content = self._create_diversity_section(results.diversity)
        domain_content = self._create_domain_section(results.domain)
        gender_content = self._create_gender_section(results.gender_bias)
        recommendations_content = self._create_recommendations_section(recommendations)
        
        # Render template
        html = template.render(
            timestamp=timestamp,
            summary_content=summary_content,
            structural_content=structural_content,
            linguistic_content=linguistic_content,
            diversity_content=diversity_content,
            domain_content=domain_content,
            gender_content=gender_content,
            recommendations_content=recommendations_content
        )
        
        return html
