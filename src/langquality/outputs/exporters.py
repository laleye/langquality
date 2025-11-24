"""Export manager for various output formats."""

import json
import csv
from pathlib import Path
from typing import Any, Dict, List

from ..pipeline.results import AnalysisResults
from ..data.models import Sentence
from ..recommendations.models import Recommendation


class ExportManager:
    """Manages exports in different formats."""
    
    def export_json(self, results: AnalysisResults, filepath: str):
        """Export results to JSON.
        
        Args:
            results: AnalysisResults object containing all analysis metrics
            filepath: Path where JSON file should be saved
        """
        # Convert results to JSON-serializable dictionary
        data = {
            "metadata": {
                "timestamp": results.timestamp.isoformat(),
                "analysis_date": results.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "config": self._serialize_config(results.config_used)
            },
            "structural": self._serialize_structural(results.structural) if results.structural else None,
            "linguistic": self._serialize_linguistic(results.linguistic) if results.linguistic else None,
            "diversity": self._serialize_diversity(results.diversity) if results.diversity else None,
            "domain": self._serialize_domain(results.domain) if results.domain else None,
            "gender_bias": self._serialize_gender_bias(results.gender_bias) if results.gender_bias else None
        }
        
        # Ensure output directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _serialize_config(self, config) -> Dict[str, Any]:
        """Serialize pipeline configuration."""
        return {
            "min_words": config.analysis.min_words,
            "max_words": config.analysis.max_words,
            "min_readability_score": config.analysis.min_readability_score,
            "max_readability_score": config.analysis.max_readability_score,
            "target_ttr": config.analysis.target_ttr,
            "min_domain_representation": config.analysis.min_domain_representation,
            "max_domain_representation": config.analysis.max_domain_representation,
            "target_gender_ratio": config.analysis.target_gender_ratio,
            "language": config.language
        }
    
    def _serialize_sentence(self, sentence: Sentence) -> Dict[str, Any]:
        """Serialize a Sentence object."""
        return {
            "text": sentence.text,
            "domain": sentence.domain,
            "source_file": sentence.source_file,
            "line_number": sentence.line_number,
            "char_count": sentence.char_count,
            "word_count": sentence.word_count,
            "metadata": sentence.metadata
        }
    
    def _serialize_structural(self, metrics) -> Dict[str, Any]:
        """Serialize structural metrics."""
        return {
            "total_sentences": metrics.total_sentences,
            "char_distribution": metrics.char_distribution,
            "word_distribution": metrics.word_distribution,
            "too_short": [self._serialize_sentence(s) for s in metrics.too_short],
            "too_long": [self._serialize_sentence(s) for s in metrics.too_long],
            "length_histogram": {str(k): v for k, v in metrics.length_histogram.items()}
        }
    
    def _serialize_linguistic(self, metrics) -> Dict[str, Any]:
        """Serialize linguistic metrics."""
        return {
            "avg_readability_score": metrics.avg_readability_score,
            "readability_distribution": metrics.readability_distribution,
            "avg_lexical_complexity": metrics.avg_lexical_complexity,
            "jargon_detected": metrics.jargon_detected,
            "complex_syntax_count": metrics.complex_syntax_count,
            "complex_sentences": [self._serialize_sentence(s) for s in metrics.complex_sentences]
        }
    
    def _serialize_diversity(self, metrics) -> Dict[str, Any]:
        """Serialize diversity metrics."""
        # Convert tuple keys to strings for JSON serialization
        bigram_dict = {" ".join(k) if isinstance(k, tuple) else str(k): v 
                       for k, v in metrics.bigram_distribution.most_common(50)}
        trigram_dict = {" ".join(k) if isinstance(k, tuple) else str(k): v 
                        for k, v in metrics.trigram_distribution.most_common(50)}
        
        return {
            "ttr": metrics.ttr,
            "unique_words": metrics.unique_words,
            "total_words": metrics.total_words,
            "vocabulary_coverage": metrics.vocabulary_coverage,
            "bigram_distribution": bigram_dict,
            "trigram_distribution": trigram_dict,
            "repetitive_ngrams": [(ng, count) for ng, count in metrics.repetitive_ngrams],
            "near_duplicates": [
                {
                    "sentence1": self._serialize_sentence(s1),
                    "sentence2": self._serialize_sentence(s2),
                    "similarity": sim
                }
                for s1, s2, sim in metrics.near_duplicates
            ],
            "sentence_starter_diversity": metrics.sentence_starter_diversity
        }
    
    def _serialize_domain(self, metrics) -> Dict[str, Any]:
        """Serialize domain metrics."""
        return {
            "domain_counts": metrics.domain_counts,
            "domain_percentages": metrics.domain_percentages,
            "underrepresented": metrics.underrepresented,
            "overrepresented": metrics.overrepresented,
            "total_domains": metrics.total_domains
        }
    
    def _serialize_gender_bias(self, metrics) -> Dict[str, Any]:
        """Serialize gender bias metrics."""
        return {
            "masculine_count": metrics.masculine_count,
            "feminine_count": metrics.feminine_count,
            "gender_ratio": metrics.gender_ratio,
            "stereotypes_detected": metrics.stereotypes_detected,
            "bias_score": metrics.bias_score,
            "total_gendered_mentions": metrics.total_gendered_mentions
        }
    
    def export_annotated_csv(self, sentences: List[Sentence], scores: Dict[str, Any], filepath: str):
        """Export annotated CSV with quality scores.
        
        Args:
            sentences: List of sentences to export
            scores: Dictionary containing quality scores for each sentence
            filepath: Path where CSV file should be saved
        """
        # Ensure output directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Write CSV file with annotations
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'text', 'domain', 'source_file', 'line_number',
                'char_count', 'word_count',
                'readability_score', 'lexical_complexity',
                'has_jargon', 'is_complex_syntax',
                'length_status', 'quality_flag'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for sentence in sentences:
                sentence_key = f"{sentence.source_file}:{sentence.line_number}"
                sentence_scores = scores.get(sentence_key, {})
                
                # Determine length status
                length_status = "ok"
                if sentence.word_count < scores.get('min_words', 3):
                    length_status = "too_short"
                elif sentence.word_count > scores.get('max_words', 20):
                    length_status = "too_long"
                
                # Determine overall quality flag
                quality_flag = "pass"
                if length_status != "ok":
                    quality_flag = "fail"
                elif sentence_scores.get('has_jargon', False):
                    quality_flag = "warning"
                elif sentence_scores.get('is_complex_syntax', False):
                    quality_flag = "warning"
                
                writer.writerow({
                    'text': sentence.text,
                    'domain': sentence.domain,
                    'source_file': sentence.source_file,
                    'line_number': sentence.line_number,
                    'char_count': sentence.char_count,
                    'word_count': sentence.word_count,
                    'readability_score': sentence_scores.get('readability_score', ''),
                    'lexical_complexity': sentence_scores.get('lexical_complexity', ''),
                    'has_jargon': sentence_scores.get('has_jargon', False),
                    'is_complex_syntax': sentence_scores.get('is_complex_syntax', False),
                    'length_status': length_status,
                    'quality_flag': quality_flag
                })
    
    def export_filtered_sentences(self, rejected: List[Dict[str, Any]], filepath: str):
        """Export filtered/rejected sentences with rejection reasons.
        
        Args:
            rejected: List of dictionaries containing rejected sentences and reasons
            filepath: Path where CSV file should be saved
        """
        # Ensure output directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Write CSV file with rejection reasons
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'text', 'domain', 'source_file', 'line_number',
                'word_count', 'rejection_reason', 'rejection_details'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in rejected:
                sentence = item.get('sentence')
                if sentence:
                    writer.writerow({
                        'text': sentence.text,
                        'domain': sentence.domain,
                        'source_file': sentence.source_file,
                        'line_number': sentence.line_number,
                        'word_count': sentence.word_count,
                        'rejection_reason': item.get('reason', 'unknown'),
                        'rejection_details': item.get('details', '')
                    })
    
    def export_pdf_report(self, results: AnalysisResults, recommendations: List[Recommendation], filepath: str):
        """Export PDF report with key visualizations and recommendations.
        
        Args:
            results: AnalysisResults object containing all analysis metrics
            recommendations: List of recommendations for improving data quality
            filepath: Path where PDF file should be saved
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")
        
        # Ensure output directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("LangQuality Analysis Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        story.append(Paragraph(f"<b>Analysis Date:</b> {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        summary_data = []
        if results.structural:
            summary_data.append(['Total Sentences', str(results.structural.total_sentences)])
            summary_data.append(['Avg Word Count', f"{results.structural.word_distribution.get('mean', 0):.1f}"])
        
        if results.diversity:
            summary_data.append(['Type-Token Ratio', f"{results.diversity.ttr:.3f}"])
            summary_data.append(['Unique Words', str(results.diversity.unique_words)])
        
        if results.domain:
            summary_data.append(['Total Domains', str(results.domain.total_domains)])
        
        if results.gender_bias:
            summary_data.append(['Gender Ratio (F/M)', f"{results.gender_bias.gender_ratio:.2f}"])
        
        if summary_data:
            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(summary_table)
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Structural Analysis
        if results.structural:
            story.append(Paragraph("Structural Analysis", heading_style))
            story.append(Paragraph(
                f"The dataset contains {results.structural.total_sentences} sentences. "
                f"The average sentence length is {results.structural.word_distribution.get('mean', 0):.1f} words, "
                f"with a median of {results.structural.word_distribution.get('median', 0):.1f} words.",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.1 * inch))
            
            issues = []
            if results.structural.too_short:
                issues.append(f"• {len(results.structural.too_short)} sentences are too short (< {results.config_used.analysis.min_words} words)")
            if results.structural.too_long:
                issues.append(f"• {len(results.structural.too_long)} sentences are too long (> {results.config_used.analysis.max_words} words)")
            
            if issues:
                story.append(Paragraph("<b>Issues Identified:</b>", styles['Normal']))
                for issue in issues:
                    story.append(Paragraph(issue, styles['Normal']))
            
            story.append(Spacer(1, 0.2 * inch))
        
        # Linguistic Analysis
        if results.linguistic:
            story.append(Paragraph("Linguistic Analysis", heading_style))
            story.append(Paragraph(
                f"The average readability score is {results.linguistic.avg_readability_score:.1f}, "
                f"with an average lexical complexity of {results.linguistic.avg_lexical_complexity:.2f}. "
                f"{results.linguistic.complex_syntax_count} sentences have complex syntax.",
                styles['Normal']
            ))
            
            if results.linguistic.jargon_detected:
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(
                    f"<b>Jargon detected in {len(results.linguistic.jargon_detected)} sentences.</b>",
                    styles['Normal']
                ))
            
            story.append(Spacer(1, 0.2 * inch))
        
        # Diversity Analysis
        if results.diversity:
            story.append(Paragraph("Diversity Analysis", heading_style))
            story.append(Paragraph(
                f"The Type-Token Ratio (TTR) is {results.diversity.ttr:.3f}, indicating "
                f"{'good' if results.diversity.ttr >= 0.6 else 'limited'} vocabulary diversity. "
                f"The dataset contains {results.diversity.unique_words} unique words out of "
                f"{results.diversity.total_words} total words.",
                styles['Normal']
            ))
            
            if results.diversity.near_duplicates:
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(
                    f"<b>Warning:</b> {len(results.diversity.near_duplicates)} near-duplicate sentence pairs detected.",
                    styles['Normal']
                ))
            
            story.append(Spacer(1, 0.2 * inch))
        
        # Domain Distribution
        if results.domain:
            story.append(Paragraph("Domain Distribution", heading_style))
            
            domain_data = [['Domain', 'Count', 'Percentage']]
            for domain, count in sorted(results.domain.domain_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = results.domain.domain_percentages.get(domain, 0)
                domain_data.append([domain, str(count), f"{percentage * 100:.1f}%"])
            
            domain_table = Table(domain_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
            domain_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
            ]))
            story.append(domain_table)
            
            if results.domain.underrepresented or results.domain.overrepresented:
                story.append(Spacer(1, 0.1 * inch))
                if results.domain.underrepresented:
                    story.append(Paragraph(
                        f"<b>Underrepresented domains:</b> {', '.join(results.domain.underrepresented)}",
                        styles['Normal']
                    ))
                if results.domain.overrepresented:
                    story.append(Paragraph(
                        f"<b>Overrepresented domains:</b> {', '.join(results.domain.overrepresented)}",
                        styles['Normal']
                    ))
            
            story.append(Spacer(1, 0.2 * inch))
        
        # Gender Bias Analysis
        if results.gender_bias:
            story.append(Paragraph("Gender Bias Analysis", heading_style))
            story.append(Paragraph(
                f"Gender ratio (F/M): {results.gender_bias.gender_ratio:.2f}. "
                f"Masculine mentions: {results.gender_bias.masculine_count}, "
                f"Feminine mentions: {results.gender_bias.feminine_count}. "
                f"Bias score: {results.gender_bias.bias_score:.2f}.",
                styles['Normal']
            ))
            
            if results.gender_bias.stereotypes_detected:
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(
                    f"<b>Warning:</b> {len(results.gender_bias.stereotypes_detected)} gender stereotypes detected.",
                    styles['Normal']
                ))
            
            story.append(Spacer(1, 0.2 * inch))
        
        # Recommendations
        if recommendations:
            story.append(PageBreak())
            story.append(Paragraph("Recommendations", heading_style))
            
            # Group by severity
            critical = [r for r in recommendations if r.severity == 'critical']
            warnings = [r for r in recommendations if r.severity == 'warning']
            info = [r for r in recommendations if r.severity == 'info']
            
            for severity_group, label, color in [
                (critical, 'Critical Issues', colors.red),
                (warnings, 'Warnings', colors.orange),
                (info, 'Suggestions', colors.blue)
            ]:
                if severity_group:
                    story.append(Paragraph(f"<b>{label}</b>", styles['Heading3']))
                    for rec in severity_group[:5]:  # Limit to top 5 per category
                        story.append(Paragraph(f"<b>{rec.title}</b>", styles['Normal']))
                        story.append(Paragraph(rec.description, styles['Normal']))
                        if rec.suggested_actions:
                            story.append(Paragraph("<i>Suggested actions:</i>", styles['Normal']))
                            for action in rec.suggested_actions[:3]:
                                story.append(Paragraph(f"• {action}", styles['Normal']))
                        story.append(Spacer(1, 0.15 * inch))
        
        # Build PDF
        doc.build(story)
    
    def create_execution_log(self, results: AnalysisResults, filepath: str):
        """Create execution log with timestamp, configuration, and summary statistics.
        
        Args:
            results: AnalysisResults object containing all analysis metrics
            filepath: Path where log file should be saved
        """
        # Ensure output directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Build log content
        log_lines = []
        log_lines.append("=" * 80)
        log_lines.append("LANGQUALITY ANALYSIS - EXECUTION LOG")
        log_lines.append("=" * 80)
        log_lines.append("")
        
        # Timestamp
        log_lines.append(f"Execution Date: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        log_lines.append(f"Timestamp: {results.timestamp.isoformat()}")
        log_lines.append("")
        
        # Configuration
        log_lines.append("-" * 80)
        log_lines.append("CONFIGURATION")
        log_lines.append("-" * 80)
        config = results.config_used.analysis
        log_lines.append(f"Language: {results.config_used.language}")
        log_lines.append(f"Min Words: {config.min_words}")
        log_lines.append(f"Max Words: {config.max_words}")
        log_lines.append(f"Min Readability Score: {config.min_readability_score}")
        log_lines.append(f"Max Readability Score: {config.max_readability_score}")
        log_lines.append(f"Target TTR: {config.target_ttr}")
        log_lines.append(f"Min Domain Representation: {config.min_domain_representation * 100}%")
        log_lines.append(f"Max Domain Representation: {config.max_domain_representation * 100}%")
        log_lines.append(f"Target Gender Ratio: {config.target_gender_ratio}")
        log_lines.append("")
        
        # Summary Statistics - Structural
        if results.structural:
            log_lines.append("-" * 80)
            log_lines.append("STRUCTURAL ANALYSIS SUMMARY")
            log_lines.append("-" * 80)
            log_lines.append(f"Total Sentences: {results.structural.total_sentences}")
            log_lines.append(f"Average Word Count: {results.structural.word_distribution.get('mean', 0):.2f}")
            log_lines.append(f"Median Word Count: {results.structural.word_distribution.get('median', 0):.2f}")
            log_lines.append(f"Std Dev Word Count: {results.structural.word_distribution.get('std', 0):.2f}")
            log_lines.append(f"Too Short Sentences: {len(results.structural.too_short)}")
            log_lines.append(f"Too Long Sentences: {len(results.structural.too_long)}")
            log_lines.append("")
        
        # Summary Statistics - Linguistic
        if results.linguistic:
            log_lines.append("-" * 80)
            log_lines.append("LINGUISTIC ANALYSIS SUMMARY")
            log_lines.append("-" * 80)
            log_lines.append(f"Average Readability Score: {results.linguistic.avg_readability_score:.2f}")
            log_lines.append(f"Average Lexical Complexity: {results.linguistic.avg_lexical_complexity:.2f}")
            log_lines.append(f"Sentences with Jargon: {len(results.linguistic.jargon_detected)}")
            log_lines.append(f"Complex Syntax Count: {results.linguistic.complex_syntax_count}")
            log_lines.append("")
        
        # Summary Statistics - Diversity
        if results.diversity:
            log_lines.append("-" * 80)
            log_lines.append("DIVERSITY ANALYSIS SUMMARY")
            log_lines.append("-" * 80)
            log_lines.append(f"Type-Token Ratio (TTR): {results.diversity.ttr:.4f}")
            log_lines.append(f"Unique Words: {results.diversity.unique_words}")
            log_lines.append(f"Total Words: {results.diversity.total_words}")
            log_lines.append(f"Vocabulary Coverage: {results.diversity.vocabulary_coverage * 100:.2f}%")
            log_lines.append(f"Near Duplicates Found: {len(results.diversity.near_duplicates)}")
            log_lines.append(f"Sentence Starter Diversity: {results.diversity.sentence_starter_diversity:.4f}")
            log_lines.append("")
        
        # Summary Statistics - Domain
        if results.domain:
            log_lines.append("-" * 80)
            log_lines.append("DOMAIN DISTRIBUTION SUMMARY")
            log_lines.append("-" * 80)
            log_lines.append(f"Total Domains: {results.domain.total_domains}")
            log_lines.append(f"Underrepresented Domains: {len(results.domain.underrepresented)}")
            if results.domain.underrepresented:
                log_lines.append(f"  - {', '.join(results.domain.underrepresented)}")
            log_lines.append(f"Overrepresented Domains: {len(results.domain.overrepresented)}")
            if results.domain.overrepresented:
                log_lines.append(f"  - {', '.join(results.domain.overrepresented)}")
            log_lines.append("")
            log_lines.append("Domain Breakdown:")
            for domain, count in sorted(results.domain.domain_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = results.domain.domain_percentages.get(domain, 0)
                log_lines.append(f"  - {domain}: {count} sentences ({percentage * 100:.1f}%)")
            log_lines.append("")
        
        # Summary Statistics - Gender Bias
        if results.gender_bias:
            log_lines.append("-" * 80)
            log_lines.append("GENDER BIAS ANALYSIS SUMMARY")
            log_lines.append("-" * 80)
            log_lines.append(f"Masculine Mentions: {results.gender_bias.masculine_count}")
            log_lines.append(f"Feminine Mentions: {results.gender_bias.feminine_count}")
            log_lines.append(f"Gender Ratio (F/M): {results.gender_bias.gender_ratio:.2f}")
            log_lines.append(f"Bias Score: {results.gender_bias.bias_score:.2f}")
            log_lines.append(f"Stereotypes Detected: {len(results.gender_bias.stereotypes_detected)}")
            log_lines.append("")
        
        log_lines.append("=" * 80)
        log_lines.append("END OF EXECUTION LOG")
        log_lines.append("=" * 80)
        
        # Write log file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(log_lines))
