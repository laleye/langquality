"""CLI interface for LangQuality.

This module provides a command-line interface for the LangQuality
Language Quality Toolkit using the Click framework.

Usage:
    # Basic analysis with language pack
    langquality analyze --language fon -i data/ -o reports/
    
    # With custom configuration
    langquality analyze --language fon -i data/ -o reports/ -c config.yaml
    
    # List available language packs
    langquality pack list
    
    # Get info about a language pack
    langquality pack info fon
    
    # Create a new language pack template
    langquality pack create xyz --name "My Language"
    
    # Validate a language pack
    langquality pack validate path/to/pack

The analyze command will:
    1. Load language pack for specified language
    2. Load configuration (from file or defaults)
    3. Load data files from input directory
    4. Run all quality analyzers
    5. Generate recommendations
    6. Export results in multiple formats:
       - Interactive HTML dashboard
       - JSON report with detailed metrics
       - Annotated CSV with quality scores
       - Filtered CSV with rejected sentences
       - PDF report with visualizations
       - Execution log
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import click

from .config.loader import load_config
from .data.generic_loader import GenericDataLoader
from .pipeline.controller import PipelineController
from .recommendations.engine import RecommendationEngine
from .recommendations.best_practices import BestPractices
from .outputs.exporters import ExportManager
from .outputs.dashboard import DashboardGenerator
from .utils.exceptions import DataLoadError, ConfigurationError
from .utils.logging import setup_logging
from .language_packs.manager import LanguagePackManager
from .language_packs.templates import LanguagePackTemplate
from .language_packs.validation import ValidationError


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """LangQuality - Language Quality Toolkit for Low-Resource Languages.
    
    A modular, extensible toolkit for analyzing the quality of text data
    for low-resource languages.
    """
    pass


@cli.command()
@click.option(
    '--language', '-l',
    'language_code',
    type=str,
    default=None,
    help='Language code (ISO 639-3) for the language pack to use (e.g., fon, eng, fra)'
)
@click.option(
    '--input', '-i',
    'input_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help='Input directory containing data files to analyze'
)
@click.option(
    '--output', '-o',
    'output_dir',
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
    help='Output directory for analysis results'
)
@click.option(
    '--config', '-c',
    'config_file',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=None,
    help='Configuration file (YAML). If not provided, uses language pack configuration'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Suppress all output except errors'
)
def analyze(language_code: Optional[str], input_dir: str, output_dir: str, 
           config_file: Optional[str], verbose: bool, quiet: bool):
    """Analyze text data quality for low-resource languages.
    
    This command loads data files from the input directory, runs all quality
    analyzers, and generates comprehensive reports including an interactive
    dashboard, JSON export, annotated CSV, and PDF report.
    
    Examples:
    
        # Analyze with Fongbe language pack
        langquality analyze --language fon -i data/ -o reports/
        
        # Analyze with custom config
        langquality analyze --language fon -i data/ -o reports/ -c config.yaml -v
        
        # Analyze without language pack (language-agnostic mode)
        langquality analyze -i data/ -o reports/
    """
    # Setup logging
    log_level = logging.ERROR if quiet else (logging.DEBUG if verbose else logging.INFO)
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Display welcome message
        if not quiet:
            click.echo("=" * 70)
            click.echo("LangQuality - Language Quality Toolkit")
            click.echo("=" * 70)
            click.echo()
        
        # Step 1: Load language pack (if specified)
        language_pack = None
        if language_code:
            if not quiet:
                click.echo(f"🌍 Loading language pack: {language_code}...")
            
            try:
                pack_manager = LanguagePackManager()
                language_pack = pack_manager.load_language_pack(language_code)
                
                if not quiet:
                    click.echo(f"✓ Loaded language pack: {language_pack.name} (v{language_pack.metadata.version})")
                    if verbose:
                        logger.info(f"Language: {language_pack.name}")
                        logger.info(f"Family: {language_pack.config.family}")
                        logger.info(f"Script: {language_pack.config.script}")
                        logger.info(f"Enabled analyzers: {language_pack.config.analyzers.enabled}")
            except FileNotFoundError as e:
                click.echo(f"❌ Language pack not found: {e}", err=True)
                click.echo("\nAvailable language packs:", err=True)
                pack_manager = LanguagePackManager()
                available = pack_manager.list_available_packs()
                for pack_code in available:
                    click.echo(f"  - {pack_code}", err=True)
                sys.exit(1)
            except ValidationError as e:
                click.echo(f"❌ Language pack validation failed: {e}", err=True)
                sys.exit(1)
            except Exception as e:
                click.echo(f"❌ Error loading language pack: {e}", err=True)
                logger.exception("Language pack loading failed")
                sys.exit(1)
        else:
            if not quiet:
                click.echo("ℹ️  No language pack specified. Running in language-agnostic mode.")
        
        # Step 2: Load configuration
        if not quiet:
            click.echo("📋 Loading configuration...")
        
        try:
            if config_file:
                config = load_config(config_file)
            elif language_pack:
                # Use language pack configuration
                config = load_config(None)  # Load defaults
                # Override with language pack thresholds if available
                if language_pack.config.thresholds.structural:
                    config.analysis.min_words = language_pack.config.thresholds.structural.min_words
                    config.analysis.max_words = language_pack.config.thresholds.structural.max_words
            else:
                config = load_config(None)
            
            # Override input/output directories from command line
            config.input_directory = input_dir
            config.output_directory = output_dir
            
            if verbose:
                logger.info("Configuration loaded successfully")
                logger.info(f"Input directory: {input_dir}")
                logger.info(f"Output directory: {output_dir}")
                logger.info(f"Enabled analyzers: {config.enable_analyzers}")
        except ConfigurationError as e:
            click.echo(f"❌ Configuration error: {e}", err=True)
            sys.exit(1)
        
        # Step 3: Load data
        if not quiet:
            click.echo(f"📂 Loading data from {input_dir}...")
        
        try:
            if language_pack:
                # Use GenericDataLoader with language pack
                data_loader = GenericDataLoader(language_pack)
            else:
                # Use GenericDataLoader without language pack (fallback mode)
                data_loader = GenericDataLoader(None)
            
            sentences_by_domain = data_loader.load_directory(input_dir)
            
            # Flatten sentences from all domains
            all_sentences = []
            for domain_sentences in sentences_by_domain.values():
                all_sentences.extend(domain_sentences)
            
            if not all_sentences:
                click.echo("❌ No sentences found in input directory", err=True)
                sys.exit(1)
            
            if not quiet:
                click.echo(f"✓ Loaded {len(all_sentences)} sentences from {len(sentences_by_domain)} domain(s)")
                if verbose:
                    for domain, sentences in sentences_by_domain.items():
                        logger.info(f"  - {domain}: {len(sentences)} sentences")
        except DataLoadError as e:
            click.echo(f"❌ Data loading error: {e}", err=True)
            sys.exit(1)
        
        # Step 4: Run pipeline analysis
        if not quiet:
            click.echo("\n🔍 Running analysis pipeline...")
        
        try:
            controller = PipelineController(config, language_pack=language_pack)
            results = controller.run(all_sentences)
            
            if not quiet:
                click.echo("✓ Analysis completed successfully")
        except Exception as e:
            click.echo(f"❌ Analysis error: {e}", err=True)
            logger.exception("Pipeline analysis failed")
            sys.exit(1)
        
        # Step 5: Generate recommendations
        if not quiet:
            click.echo("\n💡 Generating recommendations...")
        
        try:
            rec_engine = RecommendationEngine(BestPractices())
            recommendations = rec_engine.generate_recommendations(results)
            
            if not quiet:
                click.echo(f"✓ Generated {len(recommendations)} recommendations")
        except Exception as e:
            logger.warning(f"Failed to generate recommendations: {e}")
            recommendations = []
        
        # Step 6: Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Step 7: Generate all outputs
        if not quiet:
            click.echo("\n📊 Generating outputs...")
        
        exporter = ExportManager()
        output_files = []
        
        # Generate JSON export
        try:
            json_path = output_path / "analysis_results.json"
            exporter.export_json(results, str(json_path))
            output_files.append(("JSON report", json_path))
            if verbose:
                logger.info(f"Generated JSON report: {json_path}")
        except Exception as e:
            logger.error(f"Failed to generate JSON export: {e}")
        
        # Generate annotated CSV
        try:
            csv_path = output_path / "annotated_sentences.csv"
            # Build scores dictionary from results
            scores = {
                'min_words': config.analysis.min_words,
                'max_words': config.analysis.max_words
            }
            
            # Add per-sentence scores if available
            if results.linguistic:
                for i, sentence in enumerate(all_sentences):
                    sentence_key = f"{sentence.source_file}:{sentence.line_number}"
                    if i < len(results.linguistic.readability_distribution):
                        scores[sentence_key] = {
                            'readability_score': results.linguistic.readability_distribution[i],
                            'has_jargon': sentence_key in results.linguistic.jargon_detected,
                            'is_complex_syntax': sentence in results.linguistic.complex_sentences
                        }
            
            exporter.export_annotated_csv(all_sentences, scores, str(csv_path))
            output_files.append(("Annotated CSV", csv_path))
            if verbose:
                logger.info(f"Generated annotated CSV: {csv_path}")
        except Exception as e:
            logger.error(f"Failed to generate annotated CSV: {e}")
        
        # Generate filtered sentences CSV
        try:
            filtered_path = output_path / "filtered_sentences.csv"
            rejected = []
            
            # Collect rejected sentences
            if results.structural:
                for sentence in results.structural.too_short:
                    rejected.append({
                        'sentence': sentence,
                        'reason': 'too_short',
                        'details': f'Only {sentence.word_count} words (min: {config.analysis.min_words})'
                    })
                for sentence in results.structural.too_long:
                    rejected.append({
                        'sentence': sentence,
                        'reason': 'too_long',
                        'details': f'{sentence.word_count} words (max: {config.analysis.max_words})'
                    })
            
            if rejected:
                exporter.export_filtered_sentences(rejected, str(filtered_path))
                output_files.append(("Filtered sentences", filtered_path))
                if verbose:
                    logger.info(f"Generated filtered sentences CSV: {filtered_path}")
        except Exception as e:
            logger.error(f"Failed to generate filtered sentences CSV: {e}")
        
        # Generate execution log
        try:
            log_path = output_path / "execution_log.txt"
            exporter.create_execution_log(results, str(log_path))
            output_files.append(("Execution log", log_path))
            if verbose:
                logger.info(f"Generated execution log: {log_path}")
        except Exception as e:
            logger.error(f"Failed to generate execution log: {e}")
        
        # Generate PDF report
        try:
            pdf_path = output_path / "quality_report.pdf"
            exporter.export_pdf_report(results, recommendations, str(pdf_path))
            output_files.append(("PDF report", pdf_path))
            if verbose:
                logger.info(f"Generated PDF report: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
        
        # Generate interactive dashboard
        try:
            dashboard_path = output_path / "dashboard.html"
            dashboard_gen = DashboardGenerator()
            dashboard_html = dashboard_gen.generate(results, recommendations)
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            
            output_files.append(("Interactive dashboard", dashboard_path))
            if verbose:
                logger.info(f"Generated dashboard: {dashboard_path}")
        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")
        
        # Step 7: Display summary
        if not quiet:
            click.echo("\n" + "=" * 70)
            click.echo("✅ Analysis Complete!")
            click.echo("=" * 70)
            click.echo()
            
            # Display key metrics
            click.echo("📈 Key Metrics:")
            if results.structural:
                click.echo(f"  • Total sentences: {results.structural.total_sentences}")
                click.echo(f"  • Average length: {results.structural.word_distribution.get('mean', 0):.1f} words")
                if results.structural.too_short or results.structural.too_long:
                    issues = len(results.structural.too_short) + len(results.structural.too_long)
                    click.echo(f"  • Length issues: {issues} sentences")
            
            if results.diversity:
                click.echo(f"  • Type-Token Ratio: {results.diversity.ttr:.3f}")
                click.echo(f"  • Unique words: {results.diversity.unique_words}")
            
            if results.domain:
                click.echo(f"  • Domains: {results.domain.total_domains}")
            
            if results.gender_bias:
                click.echo(f"  • Gender ratio (F/M): {results.gender_bias.gender_ratio:.2f}")
            
            # Display top recommendations
            if recommendations:
                click.echo()
                click.echo("🔔 Top Recommendations:")
                critical = [r for r in recommendations if r.severity == 'critical']
                warnings = [r for r in recommendations if r.severity == 'warning']
                
                if critical:
                    click.echo(f"  • {len(critical)} critical issue(s)")
                if warnings:
                    click.echo(f"  • {len(warnings)} warning(s)")
                
                # Show top 3 recommendations
                for i, rec in enumerate(recommendations[:3], 1):
                    severity_icon = "🔴" if rec.severity == "critical" else "🟡" if rec.severity == "warning" else "🔵"
                    click.echo(f"  {severity_icon} {rec.title}")
            
            # Display output files
            click.echo()
            click.echo("📁 Generated Files:")
            for label, path in output_files:
                click.echo(f"  • {label}: {path}")
            
            click.echo()
            click.echo("💡 Open the dashboard.html file in your browser to explore the results!")
            click.echo()
        
    except KeyboardInterrupt:
        click.echo("\n\nAnalysis interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.group()
def pack():
    """Manage language packs.
    
    Commands for listing, inspecting, creating, and validating language packs.
    """
    pass


@pack.command('list')
def pack_list():
    """List all available language packs.
    
    Shows all installed language packs with their basic information.
    
    Example:
    
        langquality pack list
    """
    try:
        pack_manager = LanguagePackManager()
        available_packs = pack_manager.list_available_packs()
        
        if not available_packs:
            click.echo("No language packs found.")
            click.echo("\nTo create a new language pack, use:")
            click.echo("  langquality pack create <language_code> --name <language_name>")
            return
        
        click.echo("Available Language Packs:")
        click.echo("=" * 70)
        
        for pack_code in available_packs:
            info = pack_manager.get_pack_info(pack_code)
            if info:
                status_icon = "✓" if info.get("status") == "stable" else "⚠" if info.get("status") == "beta" else "🔧"
                click.echo(f"\n{status_icon} {pack_code} - {info.get('name', 'Unknown')}")
                click.echo(f"   Version: {info.get('version', 'Unknown')}")
                click.echo(f"   Status: {info.get('status', 'Unknown')}")
                if info.get('description'):
                    click.echo(f"   Description: {info.get('description')}")
            else:
                click.echo(f"\n• {pack_code}")
        
        click.echo("\n" + "=" * 70)
        click.echo(f"Total: {len(available_packs)} language pack(s)")
        click.echo("\nTo see details about a pack, use:")
        click.echo("  langquality pack info <language_code>")
        
    except Exception as e:
        click.echo(f"❌ Error listing language packs: {e}", err=True)
        sys.exit(1)


@pack.command('info')
@click.argument('language_code')
def pack_info(language_code: str):
    """Show detailed information about a language pack.
    
    Displays comprehensive information about a specific language pack including
    metadata, configuration, available resources, and enabled analyzers.
    
    Example:
    
        langquality pack info fon
    """
    try:
        pack_manager = LanguagePackManager()
        
        # Try to load the pack
        try:
            language_pack = pack_manager.load_language_pack(language_code, validate=False)
        except FileNotFoundError:
            click.echo(f"❌ Language pack '{language_code}' not found.", err=True)
            click.echo("\nAvailable language packs:", err=True)
            available = pack_manager.list_available_packs()
            for pack_code in available:
                click.echo(f"  - {pack_code}", err=True)
            sys.exit(1)
        
        # Display pack information
        click.echo("=" * 70)
        click.echo(f"Language Pack: {language_pack.name} ({language_pack.code})")
        click.echo("=" * 70)
        
        # Metadata
        click.echo("\n📋 Metadata:")
        click.echo(f"  Version: {language_pack.metadata.version}")
        click.echo(f"  Status: {language_pack.metadata.status}")
        click.echo(f"  Author: {language_pack.metadata.author}")
        click.echo(f"  License: {language_pack.metadata.license}")
        if language_pack.metadata.description:
            click.echo(f"  Description: {language_pack.metadata.description}")
        click.echo(f"  Created: {language_pack.metadata.created}")
        click.echo(f"  Updated: {language_pack.metadata.updated}")
        
        if language_pack.metadata.contributors:
            click.echo(f"  Contributors: {', '.join(language_pack.metadata.contributors)}")
        
        # Language configuration
        click.echo("\n🌍 Language Configuration:")
        click.echo(f"  Family: {language_pack.config.family}")
        click.echo(f"  Script: {language_pack.config.script}")
        click.echo(f"  Direction: {language_pack.config.direction}")
        click.echo(f"  Tokenization: {language_pack.config.tokenization.method}")
        if language_pack.config.tokenization.model:
            click.echo(f"  Tokenization Model: {language_pack.config.tokenization.model}")
        
        # Analyzers
        click.echo("\n🔍 Analyzers:")
        click.echo(f"  Enabled: {', '.join(language_pack.config.analyzers.enabled)}")
        if language_pack.config.analyzers.disabled:
            click.echo(f"  Disabled: {', '.join(language_pack.config.analyzers.disabled)}")
        
        # Resources
        click.echo("\n📚 Resources:")
        resource_count = 0
        if language_pack.resources:
            for resource_name, resource_data in language_pack.resources.items():
                if resource_data is not None:
                    resource_count += 1
                    if isinstance(resource_data, list):
                        click.echo(f"  ✓ {resource_name}: {len(resource_data)} items")
                    elif isinstance(resource_data, dict):
                        click.echo(f"  ✓ {resource_name}: {len(resource_data)} entries")
                    else:
                        click.echo(f"  ✓ {resource_name}: available")
        
        if resource_count == 0:
            click.echo("  No resources loaded")
        
        # Coverage
        if language_pack.metadata.coverage:
            click.echo("\n📊 Coverage:")
            coverage = language_pack.metadata.coverage
            if coverage.get('lexicon_size'):
                click.echo(f"  Lexicon Size: {coverage['lexicon_size']} words")
            if coverage.get('domains_covered'):
                domains = coverage['domains_covered']
                if domains:
                    click.echo(f"  Domains: {', '.join(domains)}")
            if 'has_gender_resources' in coverage:
                status = "Yes" if coverage['has_gender_resources'] else "No"
                click.echo(f"  Gender Resources: {status}")
        
        # References
        if language_pack.metadata.references:
            click.echo("\n🔗 References:")
            for ref in language_pack.metadata.references:
                click.echo(f"  - {ref}")
        
        # Pack location
        click.echo(f"\n📁 Location: {language_pack.pack_path}")
        
        click.echo("\n" + "=" * 70)
        
    except Exception as e:
        click.echo(f"❌ Error loading language pack info: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@pack.command('create')
@click.argument('language_code')
@click.option(
    '--name', '-n',
    'language_name',
    required=True,
    help='Full name of the language (e.g., "Fongbe", "English")'
)
@click.option(
    '--output', '-o',
    'output_dir',
    type=click.Path(file_okay=False, dir_okay=True),
    default='.',
    help='Output directory where the pack will be created (default: current directory)'
)
@click.option(
    '--author',
    default='Your Name',
    help='Pack author name'
)
@click.option(
    '--email',
    default='your.email@example.com',
    help='Author email address'
)
@click.option(
    '--minimal',
    is_flag=True,
    help='Create minimal template (only required files)'
)
def pack_create(language_code: str, language_name: str, output_dir: str,
               author: str, email: str, minimal: bool):
    """Create a new language pack template.
    
    Creates a complete directory structure with configuration files and
    example resources for a new language pack.
    
    Examples:
    
        # Create a complete language pack template
        langquality pack create xyz --name "My Language"
        
        # Create a minimal template
        langquality pack create xyz --name "My Language" --minimal
        
        # Specify author and output directory
        langquality pack create xyz --name "My Language" --author "John Doe" --email "john@example.com" -o packs/
    """
    try:
        # Validate language code format (ISO 639-3: 3 lowercase letters)
        if not language_code.isalpha() or len(language_code) != 3:
            click.echo(
                f"❌ Invalid language code '{language_code}'. "
                "Language codes must be 3 lowercase letters (ISO 639-3).",
                err=True
            )
            sys.exit(1)
        
        language_code = language_code.lower()
        output_path = Path(output_dir)
        
        # Check if pack already exists
        pack_path = output_path / language_code
        if pack_path.exists():
            click.echo(f"❌ Language pack directory already exists: {pack_path}", err=True)
            sys.exit(1)
        
        click.echo(f"Creating language pack template for '{language_name}' ({language_code})...")
        
        # Create the template
        created_path = LanguagePackTemplate.create_template(
            language_code=language_code,
            language_name=language_name,
            output_dir=output_path,
            author=author,
            email=email,
            minimal=minimal
        )
        
        click.echo(f"✓ Language pack template created at: {created_path}")
        click.echo("\nNext steps:")
        click.echo(f"  1. Edit {created_path}/config.yaml to customize configuration")
        click.echo(f"  2. Edit {created_path}/metadata.json to update metadata")
        click.echo(f"  3. Add language-specific resources to {created_path}/resources/")
        click.echo(f"  4. Validate the pack: langquality pack validate {created_path}")
        click.echo(f"  5. Test the pack: langquality analyze --language {language_code} -i data/ -o output/")
        
    except Exception as e:
        click.echo(f"❌ Error creating language pack: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@pack.command('validate')
@click.argument('pack_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed validation information'
)
def pack_validate(pack_path: str, verbose: bool):
    """Validate a language pack structure and content.
    
    Checks that a language pack has all required files, valid configuration,
    and proper structure. Reports any errors or warnings.
    
    Example:
    
        langquality pack validate path/to/language_pack
        
        langquality pack validate path/to/language_pack --verbose
    """
    try:
        pack_path_obj = Path(pack_path)
        pack_name = pack_path_obj.name
        
        click.echo(f"Validating language pack: {pack_name}")
        click.echo("=" * 70)
        
        pack_manager = LanguagePackManager()
        is_valid, errors, warnings = pack_manager.validate_pack(pack_path_obj)
        
        # Display warnings
        if warnings:
            click.echo("\n⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"  - {warning}")
        
        # Display errors
        if errors:
            click.echo("\n❌ Errors:")
            for error in errors:
                click.echo(f"  - {error}")
        
        # Display result
        click.echo("\n" + "=" * 70)
        if is_valid:
            click.echo("✅ Validation passed!")
            if warnings:
                click.echo(f"   ({len(warnings)} warning(s))")
            click.echo("\nThe language pack is ready to use.")
        else:
            click.echo("❌ Validation failed!")
            click.echo(f"   {len(errors)} error(s), {len(warnings)} warning(s)")
            click.echo("\nPlease fix the errors before using this language pack.")
            sys.exit(1)
        
        # If verbose, try to load and display pack info
        if verbose and is_valid:
            click.echo("\n" + "=" * 70)
            click.echo("Detailed Pack Information:")
            click.echo("=" * 70)
            
            try:
                # Try to load the pack
                language_pack = pack_manager.load_language_pack(pack_name, validate=False)
                
                click.echo(f"\nLanguage: {language_pack.name}")
                click.echo(f"Code: {language_pack.code}")
                click.echo(f"Version: {language_pack.metadata.version}")
                click.echo(f"Status: {language_pack.metadata.status}")
                click.echo(f"Enabled Analyzers: {', '.join(language_pack.config.analyzers.enabled)}")
                
                resource_count = sum(1 for r in language_pack.resources.values() if r is not None)
                click.echo(f"Loaded Resources: {resource_count}")
                
            except Exception as e:
                click.echo(f"\nNote: Could not load pack for detailed info: {e}")
        
    except Exception as e:
        click.echo(f"❌ Error during validation: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main CLI entry point."""
    cli()
