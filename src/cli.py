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
# MAIN ENTRY POINT
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
