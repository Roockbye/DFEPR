#!/usr/bin/env python3
"""
DFEPR - Command-Line Interface
Main entry point for DFEPR forensic laboratory
"""

import click
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Import modules
from src.chain_of_custody import ChainOfCustody, CustodyAction, EvidenceRegistry
from src.hash_verifier import HashVerifier
from src.file_recovery import FileRecoveryManager
from src.report_generator import ReportGenerator, InvestigationReport, CaseInfo
from src.utilities import Logger, ValidationHelper, TimestampHelper, SystemHelper
from src.recovery import RecoveryManager, RecoveryTool, get_recovery_manager
from src.reports import ReportGenerator as ReportsGenerator, ReportFormat, get_report_generator
from src.optimization import get_optimizer
from src.analytics import get_analytics


@click.group()
@click.version_option(version="1.0.0", prog_name="DFEPR")
@click.pass_context
def cli(ctx):
    """
    DFEPR - Digital Forensics Evidence Preservation & Recovery Lab
    
    Complete forensic investigation suite with ACPO compliance
    """
    ctx.ensure_object(dict)


@cli.group()
def case():
    """Manage forensic cases"""
    pass


@cli.group()
def evidence():
    """Manage evidence and chain of custody"""
    pass


@cli.group()
def hash():
    """Manage hash verification and integrity"""
    pass


@cli.group()
def recovery():
    """Manage file recovery operations"""
    pass


@cli.group()
def report():
    """Generate forensic reports"""
    pass


@cli.group()
def tools():
    """System tools and utilities"""
    pass


@cli.group()
def optimize():
    """Database optimization and performance tuning"""
    pass


@cli.group()
def analyze():
    """Advanced forensic analytics and pattern detection"""
    pass


# ============================================================================
# CASE COMMANDS
# ============================================================================

@case.command("create")
@click.option("--case-id", required=True, help="Case identifier (e.g., THEFT_2026_000001)")
@click.option("--case-name", required=True, help="Case name/description")
@click.option("--officer", required=True, help="Case officer name")
@click.option("--agency", required=True, help="Reporting agency")
def case_create(case_id: str, case_name: str, officer: str, agency: str):
    """Create a new forensic case"""
    
    # Validate case ID format
    if not ValidationHelper.validate_case_id(case_id):
        click.secho(f"✗ Invalid case ID format: {case_id}", fg="red", bold=True)
        click.echo("Expected format: TYPE_YEAR_NUMBER (e.g., THEFT_2026_000001)")
        sys.exit(1)
    
    # Create case directory
    case_dir = Path("evidence/cases") / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Create case metadata
    metadata = {
        "case_id": case_id,
        "case_name": case_name,
        "case_officer": officer,
        "reporting_agency": agency,
        "created": TimestampHelper.get_utc_timestamp(),
        "status": "active"
    }
    
    metadata_path = case_dir / "case_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    click.secho(f"✓ Case created: {case_id}", fg="green", bold=True)
    click.echo(f"  Directory: {case_dir}")
    click.echo(f"  Officer: {officer}")
    click.echo(f"  Agency: {agency}")


@case.command("list")
def case_list():
    """List all active cases"""
    cases_dir = Path("evidence/cases")
    
    if not cases_dir.exists():
        click.echo("No cases found")
        return
    
    cases = [d for d in cases_dir.iterdir() if d.is_dir()]
    
    if not cases:
        click.echo("No cases found")
        return
    
    click.echo(f"\n{'Case ID':<30} {'Evidence':<10} {'Created'}")
    click.echo("-" * 60)
    
    for case_dir in sorted(cases):
        metadata_path = case_dir / "case_metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
            
            # Count evidence files
            coc_files = list(case_dir.glob("*_coc.json"))
            evidence_count = len(coc_files)
            
            created = metadata.get("created", "Unknown")[:10]
            click.echo(f"{case_dir.name:<30} {evidence_count:<10} {created}")


# ============================================================================
# EVIDENCE COMMANDS
# ============================================================================

@evidence.command("register")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--evidence-id", required=True, help="Evidence identifier")
@click.option("--description", required=True, help="Evidence description")
@click.option("--source", required=True, help="Source of evidence")
@click.option("--md5", required=True, help="MD5 hash")
@click.option("--sha256", required=True, help="SHA256 hash")
@click.option("--acquirer", default="Unknown", help="Person who acquired evidence")
def evidence_register(case_id: str, evidence_id: str, description: str, 
                     source: str, md5: str, sha256: str, acquirer: str):
    """Register new evidence in registry"""
    
    # Validate case ID
    if not ValidationHelper.validate_case_id(case_id):
        click.secho("✗ Invalid case ID", fg="red")
        sys.exit(1)
    
    # Validate hash formats
    if not ValidationHelper.validate_hash(md5, "md5"):
        click.secho("✗ Invalid MD5 hash format", fg="red")
        sys.exit(1)
    
    if not ValidationHelper.validate_hash(sha256, "sha256"):
        click.secho("✗ Invalid SHA256 hash format", fg="red")
        sys.exit(1)
    
    registry = EvidenceRegistry()
    result = registry.register_evidence(
        evidence_id=evidence_id,
        case_id=case_id,
        description=description,
        source=source,
        hash_md5=md5,
        hash_sha256=sha256,
        acquirer=acquirer
    )
    
    if result:
        click.secho(f"✓ Evidence registered: {evidence_id}", fg="green", bold=True)
    else:
        click.secho(f"✗ Failed to register evidence", fg="red")
        sys.exit(1)


@evidence.command("coc-add")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--evidence-id", required=True, help="Evidence identifier")
@click.option("--action", required=True, type=click.Choice([a.value for a in CustodyAction]),
              help="Action type")
@click.option("--person", required=True, help="Person performing action")
@click.option("--title", required=True, help="Person title")
@click.option("--location", required=True, help="Location")
@click.option("--description", required=True, help="Action description")
@click.option("--items", multiple=True, required=True, help="Items affected")
@click.option("--signature", default="", help="Signature reference")
@click.option("--notes", default="", help="Additional notes")
def evidence_coc_add(case_id: str, evidence_id: str, action: str, person: str,
                    title: str, location: str, description: str, items: tuple,
                    signature: str, notes: str):
    """Add entry to chain of custody"""
    
    coc = ChainOfCustody(case_id, evidence_id)
    
    try:
        coc.add_entry(
            action=CustodyAction(action),
            person_name=person,
            person_title=title,
            location=location,
            description=description,
            items_affected=list(items),
            signature=signature,
            notes=notes
        )
        
        click.secho(f"✓ Chain of custody entry added", fg="green")
        click.echo(f"  Timestamp: {TimestampHelper.get_readable_timestamp()}")
        click.echo(f"  Action: {action}")
        click.echo(f"  Person: {person}")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@evidence.command("coc-report")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--evidence-id", required=True, help="Evidence identifier")
@click.option("--output", default=None, help="Output file path")
def evidence_coc_report(case_id: str, evidence_id: str, output: Optional[str]):
    """Generate chain of custody report"""
    
    coc = ChainOfCustody(case_id, evidence_id)
    report = coc.generate_report()
    
    if output:
        with open(output, "w") as f:
            f.write(report)
        click.secho(f"✓ Report saved: {output}", fg="green")
    else:
        click.echo(report)


# ============================================================================
# HASH COMMANDS
# ============================================================================

@hash.command("calculate")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--algorithms", multiple=True, default=["md5", "sha256"],
              help="Hash algorithms")
def hash_calculate(filepath: str, algorithms: tuple):
    """Calculate file hashes"""
    
    verifier = HashVerifier("adhoc")
    
    try:
        hashes = verifier.calculate_hash(filepath, list(algorithms))
        
        click.secho(f"File: {filepath}", bold=True)
        click.echo(f"Size: {SystemHelper.format_bytes(Path(filepath).stat().st_size)}\n")
        
        for algo, hash_val in hashes.items():
            click.echo(f"{algo.upper():<8}: {hash_val}")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@hash.command("verify")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--expected", required=True, help="Expected hash value")
@click.option("--algorithm", default="sha256", help="Hash algorithm")
def hash_verify(filepath: str, expected: str, algorithm: str):
    """Verify file hash"""
    
    verifier = HashVerifier("adhoc")
    
    try:
        is_valid, actual = verifier.verify_file_hash(filepath, expected, algorithm)
        
        status = "✓ PASS" if is_valid else "✗ FAIL"
        color = "green" if is_valid else "red"
        
        click.secho(status, fg=color, bold=True)
        click.echo(f"Algorithm: {algorithm.upper()}")
        click.echo(f"Expected:  {expected}")
        click.echo(f"Actual:    {actual}")
        
        sys.exit(0 if is_valid else 1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# RECOVERY COMMANDS
# ============================================================================

@recovery.command("tools")
def recovery_tools():
    """Check available recovery tools"""
    
    try:
        # Get a recovery manager instance to check tools
        rm = get_recovery_manager("TEST", "TEST")
        available = rm.list_available_tools()
        
        click.echo("Available Recovery Tools:\n")
        
        for tool_name, is_available in available.items():
            status = "✓" if is_available else "✗"
            color = "green" if is_available else "red"
            click.secho(f"{status} {tool_name:<20}", fg=color)
        
        tools_available = sum(1 for v in available.values() if v)
        click.echo(f"\nAvailable: {tools_available}/{len(available)} tools")
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@recovery.command("start")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--evidence-id", required=True, help="Evidence identifier")
@click.option("--source", required=True, help="Source file/device path")
@click.option("--tool", required=True, type=click.Choice(["photorec", "scalpel", "tsk"]),
              help="Recovery tool to use")
@click.option("--output-dir", default=None, help="Output directory (optional)")
def recovery_start(case_id: str, evidence_id: str, source: str, tool: str, output_dir: Optional[str]):
    """Start a file recovery operation"""
    
    try:
        # Validate case and evidence IDs
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        if not ValidationHelper.validate_evidence_id(evidence_id):
            click.secho(f"✗ Invalid evidence ID: {evidence_id}", fg="red")
            sys.exit(1)
        
        # Validate source exists
        if not Path(source).exists():
            click.secho(f"✗ Source not found: {source}", fg="red")
            sys.exit(1)
        
        # Map tool name to enum
        tool_map = {
            "photorec": RecoveryTool.PHOTOREC,
            "scalpel": RecoveryTool.SCALPEL,
            "tsk": RecoveryTool.TSK_RECOVER
        }
        
        selected_tool = tool_map.get(tool)
        
        # Start recovery
        rm = get_recovery_manager(case_id, evidence_id)
        result = rm.start_recovery(source, selected_tool, output_dir)
        
        if result.get("success"):
            click.secho(f"✓ Recovery started successfully", fg="green", bold=True)
            click.echo(f"  Recovery ID: {result.get('recovery_id')}")
            click.echo(f"  Tool: {result.get('tool')}")
            click.echo(f"  Files recovered: {result.get('files_recovered')}")
            click.echo(f"  Size: {SystemHelper.format_bytes(result.get('size_bytes', 0))}")
            click.echo(f"  Output: {result.get('output_dir')}")
            click.echo(f"  Timestamp: {result.get('timestamp')}")
        else:
            click.secho(f"✗ Recovery failed: {result.get('error')}", fg="red")
            sys.exit(1)
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@recovery.command("status")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--evidence-id", required=True, help="Evidence identifier")
def recovery_status(case_id: str, evidence_id: str):
    """Check recovery operation status"""
    
    try:
        # Validate IDs
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        recovery_dir = Path.home() / ".dfepr" / "recoveries"
        
        if not recovery_dir.exists():
            click.echo("No recovery operations found")
            return
        
        # List recovery operations for this case/evidence
        recovery_id_prefix = f"REC_{case_id}_{evidence_id}_"
        recoveries = [d for d in recovery_dir.iterdir() 
                     if d.is_dir() and d.name.startswith(recovery_id_prefix)]
        
        if not recoveries:
            click.echo(f"No recovery operations found for {case_id}/{evidence_id}")
            return
        
        click.echo(f"\nRecovery Operations for {case_id}/{evidence_id}\n")
        click.echo(f"{'Recovery ID':<50} {'Status':<15} {'Files':<10} {'Size'}")
        click.echo("-" * 85)
        
        for recovery in sorted(recoveries):
            files_count = sum(1 for _ in recovery.rglob('*') if _.is_file())
            size_bytes = sum(_.stat().st_size for _ in recovery.rglob('*') if _.is_file())
            
            click.echo(f"{recovery.name:<50} {'completed':<15} {files_count:<10} "
                      f"{SystemHelper.format_bytes(size_bytes)}")
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@recovery.command("results")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--evidence-id", required=True, help="Evidence identifier")
@click.option("--recovery-id", default=None, help="Specific recovery ID (optional)")
@click.option("--output-file", default=None, help="Save results to file")
def recovery_results(case_id: str, evidence_id: str, recovery_id: Optional[str], output_file: Optional[str]):
    """Display recovery results and recovered files"""
    
    try:
        # Validate IDs
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        recovery_dir = Path.home() / ".dfepr" / "recoveries"
        
        if not recovery_dir.exists():
            click.echo("No recovery operations found")
            return
        
        # Find recovery directory
        if recovery_id:
            target_dir = recovery_dir / recovery_id
        else:
            # Find latest recovery for this case/evidence
            recovery_id_prefix = f"REC_{case_id}_{evidence_id}_"
            recoveries = sorted([d for d in recovery_dir.iterdir() 
                               if d.is_dir() and d.name.startswith(recovery_id_prefix)],
                              reverse=True)
            
            if not recoveries:
                click.echo(f"No recovery operations found")
                return
            
            target_dir = recoveries[0]
            recovery_id = target_dir.name
        
        if not target_dir.exists():
            click.secho(f"✗ Recovery not found: {recovery_id}", fg="red")
            sys.exit(1)
        
        # Gather results
        recovered_files = []
        total_size = 0
        
        for item in target_dir.rglob('*'):
            if item.is_file():
                file_size = item.stat().st_size
                recovered_files.append({
                    "name": item.name,
                    "path": str(item.relative_to(target_dir)),
                    "size": file_size,
                    "size_formatted": SystemHelper.format_bytes(file_size)
                })
                total_size += file_size
        
        # Format output
        output_lines = []
        output_lines.append(f"Recovery Results: {recovery_id}\n")
        output_lines.append(f"Case: {case_id}")
        output_lines.append(f"Evidence: {evidence_id}")
        output_lines.append(f"Total Files: {len(recovered_files)}")
        output_lines.append(f"Total Size: {SystemHelper.format_bytes(total_size)}\n")
        output_lines.append(f"{'File Name':<40} {'Size':<15} {'Path'}")
        output_lines.append("-" * 85)
        
        for file_info in sorted(recovered_files, key=lambda x: x['name']):
            output_lines.append(f"{file_info['name']:<40} {file_info['size_formatted']:<15} "
                              f"{file_info['path']}")
        
        output_text = "\n".join(output_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_text)
            click.secho(f"✓ Results saved to {output_file}", fg="green")
        else:
            click.echo("\n" + output_text)
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# TOOLS COMMANDS
# ============================================================================

@tools.command("check")
def tools_check():
    """Check if forensic tools are installed"""
    
    required_tools = [
        "ddrescue",
        "md5sum",
        "sha256sum",
        "file",
        "fls",
        "istat",
        "icat"
    ]
    
    click.echo("Checking forensic tools...\n")
    
    available = 0
    for tool in required_tools:
        exists = SystemHelper.check_tool_available(tool)
        status = "✓" if exists else "✗"
        color = "green" if exists else "red"
        click.secho(f"{status} {tool:<20}", fg=color)
        if exists:
            available += 1
    
    click.echo(f"\nAvailable: {available}/{len(required_tools)} tools")


@tools.command("info")
def tools_info():
    """Show system information"""
    
    click.echo("System Information\n")
    
    # Disk space
    space = SystemHelper.get_disk_space(".")
    if "error" not in space:
        total = SystemHelper.format_bytes(space["total"])
        used = SystemHelper.format_bytes(space["used"])
        free = SystemHelper.format_bytes(space["free"])
        percent = space["percent_used"]
        
        click.echo(f"Disk Space:")
        click.echo(f"  Total:  {total}")
        click.echo(f"  Used:   {used} ({percent:.1f}%)")
        click.echo(f"  Free:   {free}")
    
    # Current time
    click.echo(f"\nTimestamp:")
    click.echo(f"  UTC:     {TimestampHelper.get_utc_timestamp()}")
    click.echo(f"  Local:   {datetime.now().isoformat()}")


# ============================================================================
# REPORT COMMANDS
# ============================================================================

@report.command("generate")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--type", "report_type", required=True, 
              type=click.Choice(["case-summary", "evidence-inventory", "analysis", "statistics"]),
              help="Report type to generate")
@click.option("--format", "output_format", default="json",
              type=click.Choice(["json", "csv", "text"]),
              help="Output format")
@click.option("--output", default=None, help="Output file path (optional)")
def report_generate(case_id: str, report_type: str, output_format: str, output: Optional[str]):
    """Generate forensic report"""
    
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        # Map format
        format_map = {
            "json": ReportFormat.JSON,
            "csv": ReportFormat.CSV,
            "text": ReportFormat.TEXT
        }
        
        report_gen = get_report_generator()
        
        # Generate appropriate report
        if report_type == "case-summary":
            result = report_gen.generate_case_summary_report(case_id, format_map[output_format])
        elif report_type == "evidence-inventory":
            result = report_gen.generate_evidence_inventory_report(case_id, format_map[output_format])
        elif report_type == "analysis":
            result = report_gen.generate_analysis_report(case_id, format_map[output_format])
        elif report_type == "statistics":
            result = report_gen.generate_statistics_report(case_id, format_map[output_format])
        else:
            result = {"success": False, "error": f"Unknown report type: {report_type}"}
        
        if result.get("success"):
            # Export to requested format
            report_data = result.get("data")
            
            export_result = None
            if output_format == "json":
                export_result = report_gen.export_to_json(report_data, output)
            elif output_format == "csv":
                export_result = report_gen.export_to_csv(report_data, output)
            elif output_format == "text":
                export_result = report_gen.export_to_text(report_data, output)
            
            if export_result:
                click.secho(f"✓ Report generated successfully", fg="green", bold=True)
                click.echo(f"  Type: {report_type}")
                click.echo(f"  Case: {case_id}")
                click.echo(f"  Format: {output_format}")
                click.echo(f"  Output: {export_result}")
            else:
                click.secho(f"✗ Failed to export report", fg="red")
                sys.exit(1)
        else:
            click.secho(f"✗ Report generation failed: {result.get('error')}", fg="red")
            sys.exit(1)
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@report.command("list")
def report_list():
    """List all generated reports"""
    
    try:
        reports_dir = Path.home() / ".dfepr" / "reports"
        
        if not reports_dir.exists():
            click.echo("No reports found")
            return
        
        reports = list(reports_dir.glob("report_*"))
        
        if not reports:
            click.echo("No reports found")
            return
        
        click.echo(f"\nGenerated Reports ({len(reports)} total)\n")
        click.echo(f"{'File Name':<40} {'Size':<10} {'Modified'}")
        click.echo("-" * 70)
        
        for report in sorted(reports, reverse=True):
            size = SystemHelper.format_bytes(report.stat().st_size)
            modified = datetime.fromtimestamp(report.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            click.echo(f"{report.name:<40} {size:<10} {modified}")
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@report.command("export")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--format", "output_format", required=True,
              type=click.Choice(["json", "csv", "text"]),
              help="Export format")
@click.option("--output", required=True, help="Output file path")
def report_export(case_id: str, output_format: str, output: str):
    """Export case data to specified format"""
    
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        # Validate output path
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_gen = get_report_generator()
        
        # Generate comprehensive data export
        if output_format == "json":
            # Combine multiple reports into single JSON
            summary = report_gen.generate_case_summary_report(case_id, ReportFormat.JSON)
            inventory = report_gen.generate_evidence_inventory_report(case_id, ReportFormat.JSON)
            
            export_data = {
                "export_timestamp": TimestampHelper.get_utc_timestamp(),
                "case_id": case_id,
                "summary": summary.get("data", {}),
                "inventory": inventory.get("data", {})
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            size = SystemHelper.format_bytes(output_path.stat().st_size)
            click.secho(f"✓ Data exported to JSON", fg="green", bold=True)
            click.echo(f"  Output: {output_path}")
            click.echo(f"  Size: {size}")
        
        elif output_format == "csv":
            inventory = report_gen.generate_evidence_inventory_report(case_id, ReportFormat.CSV)
            export_file = report_gen.export_to_csv(inventory.get("data", {}), str(output_path))
            
            if export_file:
                size = SystemHelper.format_bytes(Path(export_file).stat().st_size)
                click.secho(f"✓ Data exported to CSV", fg="green", bold=True)
                click.echo(f"  Output: {export_file}")
                click.echo(f"  Size: {size}")
            else:
                click.secho(f"✗ CSV export failed", fg="red")
                sys.exit(1)
        
        elif output_format == "text":
            summary = report_gen.generate_case_summary_report(case_id,ReportFormat.TEXT)
            export_file = report_gen.export_to_text(summary.get("data", {}), str(output_path))
            
            if export_file:
                size = SystemHelper.format_bytes(Path(export_file).stat().st_size)
                click.secho(f"✓ Data exported to TEXT", fg="green", bold=True)
                click.echo(f"  Output: {export_file}")
                click.echo(f"  Size: {size}")
            else:
                click.secho(f"✗ TEXT export failed", fg="red")
                sys.exit(1)
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# OPTIMIZATION COMMANDS
# ============================================================================

@optimize.command("init-indexes")
def optimize_init_indexes():
    """Initialize database indexes for performance optimization"""
    try:
        optimizer = get_optimizer()
        results = optimizer.create_optimized_indexes()
        
        click.secho("✓ Database indexes initialized", fg="green", bold=True)
        for index_name, success in results.items():
            status = "✓" if success else "✗"
            click.echo(f"  {status} {index_name}")
            
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@optimize.command("batch-import")
@click.option("--file", "import_file", required=True, type=click.Path(exists=True),
              help="JSON file with evidence items to import")
def optimize_batch_import(import_file: str):
    """Batch import evidence items from JSON file"""
    try:
        with open(import_file, 'r') as f:
            evidence_items = json.load(f)
        
        if not isinstance(evidence_items, list):
            evidence_items = [evidence_items]
        
        optimizer = get_optimizer()
        successful, failed = optimizer.batch_register_evidence(evidence_items)
        
        click.secho(f"✓ Batch import completed", fg="green", bold=True)
        click.echo(f"  Successful: {successful}")
        click.echo(f"  Failed: {failed}")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@optimize.command("performance-report")
def optimize_performance_report():
    """Display database performance metrics"""
    try:
        optimizer = get_optimizer()
        stats = optimizer.optimize_queries()
        report = optimizer.get_performance_report()
        
        click.secho("✓ Performance Report", fg="green", bold=True)
        click.echo(f"  Total cases: {stats.get('total_cases', 0)}")
        click.echo(f"  Total evidence items: {stats.get('total_evidence', 0)}")
        click.echo(f"  Total CoC entries: {stats.get('total_coc_entries', 0)}")
        click.echo()
        click.echo(f"  Operations processed: {report.get('total_operations', 0)}")
        click.echo(f"  Items processed: {report.get('total_items_processed', 0)}")
        click.echo(f"  Total time (ms): {report.get('total_time_ms', 0):.2f}")
        click.echo(f"  Avg throughput: {report.get('average_items_per_second', 0):.2f} items/sec")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@optimize.command("load-test")
@click.option("--count", default=100, type=int, help="Number of evidence items to create")
@click.option("--case-id", required=True, help="Case ID for test items")
def optimize_load_test(count: int, case_id: str):
    """Perform load test with specified number of evidence items"""
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        # Generate test evidence items
        evidence_items = []
        for i in range(count):
            evidence_items.append({
                'evidence_id': f"{case_id}_LOAD_TEST_{i:04d}",
                'case_id': case_id,
                'description': f'Load test evidence item {i}',
                'source': 'load_test',
                'status': 'created'
            })
        
        optimizer = get_optimizer()
        successful, failed = optimizer.batch_register_evidence(evidence_items)
        
        click.secho(f"✓ Load test completed", fg="green", bold=True)
        click.echo(f"  Items requested: {count}")
        click.echo(f"  Items created: {successful}")
        click.echo(f"  Items failed: {failed}")
        
        # Show performance metrics
        report = optimizer.get_performance_report()
        if report.get('metrics'):
            last_metric = report['metrics'][-1]
            click.echo()
            click.echo(f"  Operation: {last_metric['operation']}")
            click.echo(f"  Duration: {last_metric['duration_ms']:.2f} ms")
            click.echo(f"  Throughput: {last_metric['items_per_second']:.2f} items/second")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# ANALYTICS COMMANDS
# ============================================================================

@analyze.command("correlations")
@click.option("--case-id", required=True, help="Case identifier")
def analyze_correlations(case_id: str):
    """Detect evidence correlations and relationships"""
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        analytics = get_analytics()
        correlations = analytics.correlate_evidence(case_id)
        
        click.secho(f"✓ Evidence correlations detected", fg="green", bold=True)
        click.echo(f"  Total correlations: {len(correlations)}")
        click.echo()
        
        if correlations:
            click.echo("Correlations:")
            for i, corr in enumerate(correlations[:10], 1):
                click.echo(f"  {i}. {corr.evidence_id_1} -- {corr.evidence_id_2}")
                click.echo(f"     Type: {corr.correlation_type.value}")
                click.echo(f"     Confidence: {corr.confidence*100:.1f}%")
            
            if len(correlations) > 10:
                click.echo(f"  ... and {len(correlations) - 10} more")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@analyze.command("anomalies")
@click.option("--case-id", required=True, help="Case identifier")
def analyze_anomalies(case_id: str):
    """Detect anomalies in evidence"""
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        analytics = get_analytics()
        anomalies = analytics.detect_anomalies(case_id)
        
        click.secho(f"✓ Anomaly detection completed", fg="green", bold=True)
        click.echo(f"  Total anomalies: {len(anomalies)}")
        click.echo()
        
        if anomalies:
            click.echo("Anomalies detected:")
            for i, anomaly in enumerate(anomalies[:10], 1):
                severity_color = "red" if anomaly.severity == "high" else "yellow"
                click.secho(f"  {i}. [{anomaly.severity.upper()}] {anomaly.anomaly_type.value}", fg=severity_color)
                click.echo(f"     Description: {anomaly.description}")
                click.echo(f"     Affected items: {', '.join(anomaly.affected_items)}")
            
            if len(anomalies) > 10:
                click.echo(f"  ... and {len(anomalies) - 10} more")
        else:
            click.echo("  No anomalies detected")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@analyze.command("timeline")
@click.option("--case-id", required=True, help="Case identifier")
def analyze_timeline(case_id: str):
    """Analyze temporal patterns in evidence"""
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        analytics = get_analytics()
        timeline = analytics.analyze_temporal_patterns(case_id)
        
        click.secho(f"✓ Temporal analysis completed", fg="green", bold=True)
        click.echo(f"  Total events: {timeline['total_events']}")
        
        if timeline['date_range']:
            dr = timeline['date_range']
            click.echo(f"  Date range: {dr['start']} to {dr['end']}")
            click.echo(f"  Duration: {dr['duration_seconds']:.0f} seconds")
        
        click.echo(f"  Average interval: {timeline['average_interval_seconds']:.2f} seconds")
        
        if timeline['timeline_gaps']:
            click.echo()
            click.echo(f"  Timeline gaps detected: {len(timeline['timeline_gaps'])}")
            for i, gap in enumerate(timeline['timeline_gaps'][:5], 1):
                click.echo(f"    {i}. {gap['gap_seconds']:.0f} seconds")
        
        if timeline['temporal_clusters']:
            click.echo()
            click.echo(f"  Temporal clusters: {len(timeline['temporal_clusters'])}")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


@analyze.command("report")
@click.option("--case-id", required=True, help="Case identifier")
@click.option("--output", default=None, type=click.Path(), help="Output file (optional)")
def analyze_report(case_id: str, output: Optional[str]):
    """Generate comprehensive analytics report"""
    try:
        # Validate case ID
        if not ValidationHelper.validate_case_id(case_id):
            click.secho(f"✗ Invalid case ID: {case_id}", fg="red")
            sys.exit(1)
        
        analytics = get_analytics()
        report = analytics.generate_analytics_report(case_id)
        
        click.secho(f"✓ Analytics report generated", fg="green", bold=True)
        click.echo(f"  Case: {report['case_id']}")
        click.echo(f"  Anomalies: {report['anomalies']}")
        click.echo(f"  Correlations: {report['correlations']}")
        
        if output:
            output_path = Path(output)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            click.echo(f"  Report saved to: {output_path}")
        else:
            click.echo()
            click.echo(json.dumps(report, indent=2, default=str))
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        sys.exit(1)


# ============================================================================

def main():
    """Main CLI entry point"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
