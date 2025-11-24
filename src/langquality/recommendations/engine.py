"""Recommendation engine implementation.

This module generates actionable recommendations based on analysis results,
helping users improve dataset quality according to best practices for ASR
and translation in low-resource languages.
"""

from typing import List

from .models import Recommendation
from .best_practices import BestPractices
from ..pipeline.results import AnalysisResults


class RecommendationEngine:
    """Generates actionable recommendations based on analysis results.
    
    The engine analyzes metrics from all analyzers and generates prioritized
    recommendations with specific actions to improve dataset quality.
    """
    
    def __init__(self, best_practices: BestPractices = None):
        """Initialize the recommendation engine.
        
        Args:
            best_practices: BestPractices instance with thresholds.
                          If None, uses default BestPractices.
        """
        self.best_practices = best_practices or BestPractices()
    
    def generate_recommendations(self, results: AnalysisResults) -> List[Recommendation]:
        """Generate recommendations from analysis results.
        
        Analyzes all metrics and generates prioritized, actionable recommendations
        for improving dataset quality.
        
        Args:
            results: AnalysisResults containing all analysis metrics
            
        Returns:
            List of Recommendation objects, sorted by priority
        """
        recommendations = []
        
        # Check structural issues (sentence length)
        if results.structural:
            recommendations.extend(self._check_length_issues(results.structural))
        
        # Check linguistic complexity issues
        if results.linguistic:
            recommendations.extend(self._check_complexity_issues(results.linguistic))
        
        # Check diversity issues
        if results.diversity:
            recommendations.extend(self._check_diversity_issues(results.diversity))
        
        # Check domain balance
        if results.domain:
            recommendations.extend(self._check_domain_balance(results.domain))
        
        # Check gender bias
        if results.gender_bias:
            recommendations.extend(self._check_gender_bias(results.gender_bias))
        
        # Prioritize and sort recommendations
        prioritized = self.prioritize_recommendations(recommendations)
        
        return prioritized
    
    def _check_length_issues(self, structural) -> List[Recommendation]:
        """Check for sentence length issues.
        
        Args:
            structural: StructuralMetrics from analysis
            
        Returns:
            List of recommendations for length issues
        """
        recommendations = []
        bp = self.best_practices
        
        # Check for too-long sentences
        if structural.too_long:
            num_long = len(structural.too_long)
            percentage = (num_long / structural.total_sentences) * 100 if structural.total_sentences > 0 else 0
            
            severity = bp.SEVERITY_CRITICAL if percentage > 20 else bp.SEVERITY_WARNING
            priority = bp.PRIORITY_CRITICAL if percentage > 20 else bp.PRIORITY_HIGH
            
            recommendations.append(Recommendation(
                category="structural",
                severity=severity,
                title=f"{num_long} sentences exceed maximum length ({bp.MAX_SENTENCE_LENGTH} words)",
                description=(
                    f"{percentage:.1f}% of sentences are too long (>{bp.MAX_SENTENCE_LENGTH} words). "
                    f"Long sentences are difficult to pronounce clearly in one breath and increase "
                    f"the risk of recording errors. Optimal length is {bp.OPTIMAL_SENTENCE_LENGTH[0]}-"
                    f"{bp.OPTIMAL_SENTENCE_LENGTH[1]} words."
                ),
                affected_items=structural.too_long[:10],  # Show first 10 examples
                suggested_actions=[
                    f"Split long sentences into shorter ones (target: {bp.OPTIMAL_SENTENCE_LENGTH[0]}-{bp.OPTIMAL_SENTENCE_LENGTH[1]} words)",
                    "Break compound sentences at natural clause boundaries",
                    "Remove unnecessary subordinate clauses",
                    "Simplify complex sentence structures"
                ],
                priority=priority
            ))
        
        # Check for too-short sentences
        if structural.too_short:
            num_short = len(structural.too_short)
            percentage = (num_short / structural.total_sentences) * 100 if structural.total_sentences > 0 else 0
            
            severity = bp.SEVERITY_WARNING if percentage > 15 else bp.SEVERITY_INFO
            priority = bp.PRIORITY_HIGH if percentage > 15 else bp.PRIORITY_MEDIUM
            
            recommendations.append(Recommendation(
                category="structural",
                severity=severity,
                title=f"{num_short} sentences are below minimum length ({bp.MIN_SENTENCE_LENGTH} words)",
                description=(
                    f"{percentage:.1f}% of sentences are too short (<{bp.MIN_SENTENCE_LENGTH} words). "
                    f"Very short sentences may lack sufficient context for meaningful translation "
                    f"and may not represent natural language use."
                ),
                affected_items=structural.too_short[:10],
                suggested_actions=[
                    f"Expand short sentences to at least {bp.MIN_SENTENCE_LENGTH} words",
                    "Add context or descriptive details",
                    "Combine related short sentences",
                    "Ensure sentences form complete thoughts"
                ],
                priority=priority
            ))
        
        # Check if average length is outside optimal range
        avg_length = structural.word_distribution.get('mean', 0)
        optimal_min, optimal_max = bp.OPTIMAL_SENTENCE_LENGTH
        
        if avg_length > 0 and (avg_length < optimal_min or avg_length > optimal_max):
            if avg_length < optimal_min:
                message = f"Average sentence length ({avg_length:.1f} words) is below optimal range"
                action = f"Increase average sentence length to {optimal_min}-{optimal_max} words"
            else:
                message = f"Average sentence length ({avg_length:.1f} words) exceeds optimal range"
                action = f"Reduce average sentence length to {optimal_min}-{optimal_max} words"
            
            recommendations.append(Recommendation(
                category="structural",
                severity=bp.SEVERITY_INFO,
                title=message,
                description=(
                    f"The dataset's average sentence length is {avg_length:.1f} words. "
                    f"For optimal ASR and translation quality, aim for {optimal_min}-{optimal_max} words per sentence."
                ),
                affected_items=[],
                suggested_actions=[
                    action,
                    "Review and adjust sentence lengths across the dataset",
                    "Focus on sentences at the extremes of the distribution"
                ],
                priority=bp.PRIORITY_MEDIUM
            ))
        
        return recommendations
    
    def _check_complexity_issues(self, linguistic) -> List[Recommendation]:
        """Check for linguistic complexity issues.
        
        Args:
            linguistic: LinguisticMetrics from analysis
            
        Returns:
            List of recommendations for complexity issues
        """
        recommendations = []
        bp = self.best_practices
        
        # Check readability score
        if linguistic.avg_readability_score > bp.MAX_READABILITY_SCORE:
            recommendations.append(Recommendation(
                category="linguistic",
                severity=bp.SEVERITY_WARNING,
                title=f"Average readability score ({linguistic.avg_readability_score:.1f}) exceeds threshold",
                description=(
                    f"The average Flesch Reading Ease score is {linguistic.avg_readability_score:.1f}, "
                    f"which exceeds the recommended maximum of {bp.MAX_READABILITY_SCORE}. "
                    f"High scores indicate text that may be too complex for clear pronunciation. "
                    f"Optimal range is {bp.OPTIMAL_READABILITY_SCORE[0]}-{bp.OPTIMAL_READABILITY_SCORE[1]}."
                ),
                affected_items=[],
                suggested_actions=[
                    "Simplify sentence structures",
                    "Use shorter, more common words",
                    "Reduce the use of subordinate clauses",
                    "Break complex ideas into simpler sentences"
                ],
                priority=bp.PRIORITY_HIGH
            ))
        
        # Check lexical complexity
        if linguistic.avg_lexical_complexity > bp.MAX_LEXICAL_COMPLEXITY:
            recommendations.append(Recommendation(
                category="linguistic",
                severity=bp.SEVERITY_WARNING,
                title=f"High lexical complexity ({linguistic.avg_lexical_complexity:.2f})",
                description=(
                    f"The average lexical complexity is {linguistic.avg_lexical_complexity:.2f}, "
                    f"exceeding the threshold of {bp.MAX_LEXICAL_COMPLEXITY}. "
                    f"This indicates frequent use of rare or technical vocabulary that may be "
                    f"difficult to pronounce or translate accurately."
                ),
                affected_items=[],
                suggested_actions=[
                    "Replace rare words with more common alternatives",
                    "Use everyday vocabulary instead of technical terms",
                    "Ensure words are in the top 5000 most frequent French words",
                    "Review and simplify specialized terminology"
                ],
                priority=bp.PRIORITY_HIGH
            ))
        
        # Check for jargon
        if linguistic.jargon_detected:
            num_sentences_with_jargon = len(linguistic.jargon_detected)
            
            # Collect all jargon terms
            all_jargon = []
            for terms in linguistic.jargon_detected.values():
                all_jargon.extend(terms)
            unique_jargon = list(set(all_jargon))
            
            recommendations.append(Recommendation(
                category="linguistic",
                severity=bp.SEVERITY_WARNING,
                title=f"Jargon detected in {num_sentences_with_jargon} sentences",
                description=(
                    f"Technical jargon or specialized terms were detected in {num_sentences_with_jargon} sentences. "
                    f"Jargon can be difficult to pronounce consistently and may not translate well. "
                    f"Examples: {', '.join(unique_jargon[:10])}"
                ),
                affected_items=unique_jargon[:20],
                suggested_actions=[
                    "Replace jargon with plain language equivalents",
                    "Define technical terms or use simpler alternatives",
                    "Ensure terminology is appropriate for general audiences",
                    "Review domain-specific vocabulary for accessibility"
                ],
                priority=bp.PRIORITY_MEDIUM
            ))
        
        # Check complex syntax
        if linguistic.complex_syntax_count > 0:
            total_sentences = len(linguistic.readability_distribution)
            percentage = (linguistic.complex_syntax_count / total_sentences) * 100 if total_sentences > 0 else 0
            
            if percentage > bp.MAX_COMPLEX_SYNTAX_PERCENTAGE * 100:
                recommendations.append(Recommendation(
                    category="linguistic",
                    severity=bp.SEVERITY_WARNING,
                    title=f"{linguistic.complex_syntax_count} sentences have complex syntax ({percentage:.1f}%)",
                    description=(
                        f"{percentage:.1f}% of sentences have complex syntactic structures "
                        f"(multiple subordinate clauses, passive voice, deep syntax trees). "
                        f"Complex syntax can lead to pronunciation difficulties and translation errors. "
                        f"Recommended maximum is {bp.MAX_COMPLEX_SYNTAX_PERCENTAGE * 100:.0f}%."
                    ),
                    affected_items=linguistic.complex_sentences[:10],
                    suggested_actions=[
                        "Simplify sentence structures",
                        "Convert passive voice to active voice",
                        "Reduce the number of subordinate clauses",
                        "Break complex sentences into simpler ones",
                        "Use direct, straightforward sentence patterns"
                    ],
                    priority=bp.PRIORITY_HIGH
                ))
        
        return recommendations
    
    def _check_diversity_issues(self, diversity) -> List[Recommendation]:
        """Check for vocabulary and structural diversity issues.
        
        Args:
            diversity: DiversityMetrics from analysis
            
        Returns:
            List of recommendations for diversity issues
        """
        recommendations = []
        bp = self.best_practices
        
        # Check Type-Token Ratio (TTR)
        if diversity.ttr < bp.MIN_TTR:
            recommendations.append(Recommendation(
                category="diversity",
                severity=bp.SEVERITY_WARNING,
                title=f"Low vocabulary diversity (TTR: {diversity.ttr:.2f})",
                description=(
                    f"The Type-Token Ratio is {diversity.ttr:.2f}, below the minimum threshold of {bp.MIN_TTR}. "
                    f"This indicates excessive vocabulary repetition. Target TTR is {bp.TARGET_TTR}. "
                    f"Dataset has {diversity.unique_words} unique words out of {diversity.total_words} total words."
                ),
                affected_items=[],
                suggested_actions=[
                    "Add sentences with more varied vocabulary",
                    "Introduce synonyms and alternative expressions",
                    "Expand coverage of different semantic domains",
                    "Avoid repeating the same words and phrases",
                    f"Aim for at least {int(diversity.total_words * bp.TARGET_TTR)} unique words"
                ],
                priority=bp.PRIORITY_HIGH
            ))
        elif diversity.ttr < bp.TARGET_TTR:
            recommendations.append(Recommendation(
                category="diversity",
                severity=bp.SEVERITY_INFO,
                title=f"Vocabulary diversity below target (TTR: {diversity.ttr:.2f})",
                description=(
                    f"The Type-Token Ratio is {diversity.ttr:.2f}, below the target of {bp.TARGET_TTR}. "
                    f"Increasing vocabulary diversity will improve dataset quality."
                ),
                affected_items=[],
                suggested_actions=[
                    "Add sentences with varied vocabulary",
                    "Introduce more diverse expressions and phrasings"
                ],
                priority=bp.PRIORITY_MEDIUM
            ))
        
        # Check vocabulary coverage
        if diversity.vocabulary_coverage > 0 and diversity.vocabulary_coverage < bp.TARGET_VOCABULARY_COVERAGE:
            recommendations.append(Recommendation(
                category="diversity",
                severity=bp.SEVERITY_WARNING,
                title=f"Low vocabulary coverage ({diversity.vocabulary_coverage:.1%})",
                description=(
                    f"The dataset covers only {diversity.vocabulary_coverage:.1%} of the reference vocabulary. "
                    f"Target coverage is {bp.TARGET_VOCABULARY_COVERAGE:.1%}. "
                    f"Low coverage indicates gaps in essential vocabulary."
                ),
                affected_items=[],
                suggested_actions=[
                    "Add sentences covering missing common words",
                    "Review reference vocabulary for gaps",
                    "Ensure coverage of essential semantic categories (numbers, time, actions)",
                    f"Aim for at least {bp.TARGET_VOCABULARY_COVERAGE:.0%} coverage"
                ],
                priority=bp.PRIORITY_HIGH
            ))
        
        # Check for repetitive n-grams
        if diversity.repetitive_ngrams:
            num_repetitive = len(diversity.repetitive_ngrams)
            top_repetitive = diversity.repetitive_ngrams[:5]
            
            # Format top repetitive n-grams for display
            top_rep_formatted = ', '.join([f'"{ng[0]}" ({ng[1]}x)' for ng in top_repetitive[:3]])
            
            recommendations.append(Recommendation(
                category="diversity",
                severity=bp.SEVERITY_WARNING,
                title=f"{num_repetitive} n-grams are highly repetitive",
                description=(
                    f"Found {num_repetitive} n-grams (word sequences) that appear more than "
                    f"{bp.MAX_NGRAM_REPETITION_COUNT} times. "
                    f"Excessive repetition reduces structural diversity. "
                    f"Most repetitive: {top_rep_formatted}"
                ),
                affected_items=[f"{ngram}: {count} occurrences" for ngram, count in top_repetitive],
                suggested_actions=[
                    "Vary sentence structures and phrasings",
                    "Replace repetitive phrases with alternatives",
                    "Avoid using the same sentence templates repeatedly",
                    "Introduce more diverse ways to express similar ideas"
                ],
                priority=bp.PRIORITY_MEDIUM
            ))
        
        # Check for near-duplicates
        if diversity.near_duplicates:
            num_duplicates = len(diversity.near_duplicates)
            total_sentences = diversity.total_words // 10  # Rough estimate
            percentage = (num_duplicates / total_sentences) * 100 if total_sentences > 0 else 0
            
            severity = bp.SEVERITY_CRITICAL if percentage > bp.MAX_NEAR_DUPLICATE_PERCENTAGE * 100 else bp.SEVERITY_WARNING
            priority = bp.PRIORITY_CRITICAL if percentage > bp.MAX_NEAR_DUPLICATE_PERCENTAGE * 100 else bp.PRIORITY_HIGH
            
            recommendations.append(Recommendation(
                category="diversity",
                severity=severity,
                title=f"{num_duplicates} near-duplicate sentence pairs detected",
                description=(
                    f"Found {num_duplicates} pairs of sentences with >{bp.NEAR_DUPLICATE_THRESHOLD:.0%} similarity. "
                    f"Near-duplicates waste resources and don't add value to the dataset. "
                    f"They should be removed or significantly modified."
                ),
                affected_items=[
                    f"'{pair[0].text[:50]}...' ≈ '{pair[1].text[:50]}...' ({pair[2]:.1%} similar)"
                    for pair in diversity.near_duplicates[:10]
                ],
                suggested_actions=[
                    "Remove duplicate sentences",
                    "Significantly modify near-duplicates to increase diversity",
                    "Review sentence collection process to avoid duplicates",
                    "Use automated duplicate detection during collection"
                ],
                priority=priority
            ))
        
        # Check sentence starter diversity
        if diversity.sentence_starter_diversity < bp.MIN_STARTER_DIVERSITY:
            recommendations.append(Recommendation(
                category="diversity",
                severity=bp.SEVERITY_INFO,
                title=f"Low sentence starter diversity ({diversity.sentence_starter_diversity:.2f})",
                description=(
                    f"Sentence starter diversity is {diversity.sentence_starter_diversity:.2f}, "
                    f"below the minimum of {bp.MIN_STARTER_DIVERSITY}. "
                    f"This indicates many sentences start with the same words, reducing structural variety."
                ),
                affected_items=[],
                suggested_actions=[
                    "Vary how sentences begin",
                    "Use different sentence structures and patterns",
                    "Avoid starting many sentences with the same words",
                    "Introduce diverse sentence openings (questions, statements, commands)"
                ],
                priority=bp.PRIORITY_LOW
            ))
        
        return recommendations
    
    def _check_domain_balance(self, domain) -> List[Recommendation]:
        """Check for domain distribution balance issues.
        
        Args:
            domain: DomainMetrics from analysis
            
        Returns:
            List of recommendations for domain balance issues
        """
        recommendations = []
        bp = self.best_practices
        
        # Check underrepresented domains
        if domain.underrepresented:
            domain_list = ', '.join(domain.underrepresented)
            
            recommendations.append(Recommendation(
                category="domain",
                severity=bp.SEVERITY_WARNING,
                title=f"{len(domain.underrepresented)} domains are underrepresented",
                description=(
                    f"The following domains have less than {bp.MIN_DOMAIN_REPRESENTATION:.0%} representation: "
                    f"{domain_list}. "
                    f"Underrepresented domains limit the dataset's coverage of different contexts and topics."
                ),
                affected_items=[
                    f"{d}: {domain.domain_counts.get(d, 0)} sentences ({domain.domain_percentages.get(d, 0):.1%})"
                    for d in domain.underrepresented
                ],
                suggested_actions=[
                    "Add more sentences for underrepresented domains",
                    f"Aim for at least {bp.MIN_DOMAIN_REPRESENTATION:.0%} representation per domain",
                    "Balance domain distribution across the dataset",
                    "Consider merging very small domains or removing them"
                ],
                priority=bp.PRIORITY_HIGH
            ))
        
        # Check overrepresented domains
        if domain.overrepresented:
            domain_list = ', '.join(domain.overrepresented)
            
            recommendations.append(Recommendation(
                category="domain",
                severity=bp.SEVERITY_WARNING,
                title=f"{len(domain.overrepresented)} domains are overrepresented",
                description=(
                    f"The following domains exceed {bp.MAX_DOMAIN_REPRESENTATION:.0%} representation: "
                    f"{domain_list}. "
                    f"Overrepresented domains can bias the dataset toward specific topics."
                ),
                affected_items=[
                    f"{d}: {domain.domain_counts.get(d, 0)} sentences ({domain.domain_percentages.get(d, 0):.1%})"
                    for d in domain.overrepresented
                ],
                suggested_actions=[
                    "Reduce sentences in overrepresented domains",
                    f"Keep domain representation below {bp.MAX_DOMAIN_REPRESENTATION:.0%}",
                    "Add sentences to other domains to balance distribution",
                    "Review if overrepresented domains are truly necessary"
                ],
                priority=bp.PRIORITY_HIGH
            ))
        
        # Check overall balance
        if domain.total_domains > 0:
            # Calculate how balanced the distribution is
            percentages = list(domain.domain_percentages.values())
            if percentages:
                max_pct = max(percentages)
                min_pct = min(percentages)
                balance_ratio = min_pct / max_pct if max_pct > 0 else 0
                
                # If the smallest domain is less than 40% of the largest, suggest rebalancing
                if balance_ratio < 0.4 and not (domain.underrepresented or domain.overrepresented):
                    recommendations.append(Recommendation(
                        category="domain",
                        severity=bp.SEVERITY_INFO,
                        title="Domain distribution could be more balanced",
                        description=(
                            f"The dataset has {domain.total_domains} domains with varying representation. "
                            f"The largest domain ({max_pct:.1%}) is significantly larger than the smallest ({min_pct:.1%}). "
                            f"More balanced distribution improves dataset quality."
                        ),
                        affected_items=[
                            f"{d}: {domain.domain_percentages[d]:.1%}"
                            for d in sorted(domain.domain_percentages, key=domain.domain_percentages.get, reverse=True)
                        ],
                        suggested_actions=[
                            "Aim for more balanced domain representation",
                            f"Target range: {bp.OPTIMAL_DOMAIN_REPRESENTATION[0]:.0%}-{bp.OPTIMAL_DOMAIN_REPRESENTATION[1]:.0%} per domain",
                            "Add sentences to smaller domains",
                            "Consider redistributing sentences across domains"
                        ],
                        priority=bp.PRIORITY_MEDIUM
                    ))
        
        return recommendations
    
    def _check_gender_bias(self, gender_bias) -> List[Recommendation]:
        """Check for gender bias issues.
        
        Args:
            gender_bias: GenderBiasMetrics from analysis
            
        Returns:
            List of recommendations for gender bias issues
        """
        recommendations = []
        bp = self.best_practices
        
        # Check gender ratio
        target_min, target_max = bp.TARGET_GENDER_RATIO
        
        if gender_bias.total_gendered_mentions > 0:
            if gender_bias.gender_ratio < target_min or gender_bias.gender_ratio > target_max:
                if gender_bias.gender_ratio < target_min:
                    bias_direction = "masculine"
                    ratio_desc = f"F/M ratio of {gender_bias.gender_ratio:.2f}"
                elif gender_bias.gender_ratio == float('inf'):
                    bias_direction = "feminine"
                    ratio_desc = "only feminine mentions"
                else:
                    bias_direction = "feminine"
                    ratio_desc = f"F/M ratio of {gender_bias.gender_ratio:.2f}"
                
                recommendations.append(Recommendation(
                    category="gender_bias",
                    severity=bp.SEVERITY_WARNING,
                    title=f"Gender imbalance detected (bias toward {bias_direction})",
                    description=(
                        f"The dataset shows gender imbalance with {ratio_desc}. "
                        f"Masculine mentions: {gender_bias.masculine_count}, "
                        f"Feminine mentions: {gender_bias.feminine_count}. "
                        f"Target ratio range is {target_min:.1f}-{target_max:.1f}. "
                        f"Balanced gender representation is important for fair and unbiased models."
                    ),
                    affected_items=[],
                    suggested_actions=[
                        f"Add more sentences with {('feminine' if bias_direction == 'masculine' else 'masculine')} references",
                        "Ensure balanced representation of all genders",
                        "Review and adjust gendered language throughout the dataset",
                        "Use gender-neutral language where appropriate",
                        f"Aim for F/M ratio between {target_min:.1f} and {target_max:.1f}"
                    ],
                    priority=bp.PRIORITY_HIGH
                ))
        
        # Check overall bias score
        if gender_bias.bias_score > bp.MAX_BIAS_SCORE:
            recommendations.append(Recommendation(
                category="gender_bias",
                severity=bp.SEVERITY_CRITICAL,
                title=f"High gender bias score ({gender_bias.bias_score:.2f})",
                description=(
                    f"The overall gender bias score is {gender_bias.bias_score:.2f}, "
                    f"exceeding the maximum threshold of {bp.MAX_BIAS_SCORE}. "
                    f"This indicates significant gender imbalance and/or stereotyping in the dataset."
                ),
                affected_items=[],
                suggested_actions=[
                    "Review and address gender imbalance",
                    "Remove or modify stereotypical content",
                    "Add balanced gender representation",
                    "Ensure fair representation across all contexts"
                ],
                priority=bp.PRIORITY_CRITICAL
            ))
        
        # Check for stereotypes
        if gender_bias.stereotypes_detected:
            num_stereotypes = len(gender_bias.stereotypes_detected)
            
            # Calculate stereotypes per 100 sentences (rough estimate)
            # Assuming average of 10 words per sentence
            estimated_sentences = gender_bias.total_gendered_mentions // 2  # Rough estimate
            stereotypes_per_100 = (num_stereotypes / estimated_sentences * 100) if estimated_sentences > 0 else 0
            
            severity = bp.SEVERITY_CRITICAL if stereotypes_per_100 > bp.MAX_STEREOTYPES_PER_100 else bp.SEVERITY_WARNING
            priority = bp.PRIORITY_CRITICAL if stereotypes_per_100 > bp.MAX_STEREOTYPES_PER_100 else bp.PRIORITY_HIGH
            
            # Group stereotypes by type
            stereotype_types = {}
            for stereotype in gender_bias.stereotypes_detected:
                stype = stereotype.get('stereotype_type', 'unknown')
                if stype not in stereotype_types:
                    stereotype_types[stype] = []
                stereotype_types[stype].append(stereotype)
            
            type_summary = ', '.join([f"{stype} ({len(items)})" for stype, items in stereotype_types.items()])
            
            recommendations.append(Recommendation(
                category="gender_bias",
                severity=severity,
                title=f"{num_stereotypes} gender stereotypes detected",
                description=(
                    f"Found {num_stereotypes} instances of gender stereotypes in the dataset. "
                    f"Types: {type_summary}. "
                    f"Stereotypes perpetuate biases and should be removed or rewritten."
                ),
                affected_items=[
                    f"{s.get('stereotype_type', 'unknown')}: {s.get('sentence', '')[:60]}... "
                    f"({s.get('source_file', '')}:{s.get('line_number', '')})"
                    for s in gender_bias.stereotypes_detected[:10]
                ],
                suggested_actions=[
                    "Remove sentences with gender stereotypes",
                    "Rewrite stereotypical content with balanced representations",
                    "Avoid associating genders with specific roles or traits",
                    "Ensure diverse and non-stereotypical portrayals",
                    "Review gendered professions for balance"
                ],
                priority=priority
            ))
        
        return recommendations
    
    def prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioritize and sort recommendations.
        
        Sorts recommendations by priority (1 = highest) and then by severity.
        
        Args:
            recommendations: List of recommendations to prioritize
            
        Returns:
            Sorted list of recommendations
        """
        # Define severity order for secondary sorting
        severity_order = {
            self.best_practices.SEVERITY_CRITICAL: 0,
            self.best_practices.SEVERITY_WARNING: 1,
            self.best_practices.SEVERITY_INFO: 2
        }
        
        # Sort by priority (ascending) then severity (critical first)
        sorted_recommendations = sorted(
            recommendations,
            key=lambda r: (r.priority, severity_order.get(r.severity, 999))
        )
        
        return sorted_recommendations
