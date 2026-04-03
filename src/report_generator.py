#!/usr/bin/env python3
"""
DFEPR - Report Generator Module
Generates court-admissible forensic investigation reports
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CaseInfo:
    """Case information"""
    case_id: str
    case_name: str
    reporting_agency: str
    case_officer: str
    incident_date: str
    report_date: str


@dataclass
class InvestigationReport:
    """Investigation report metadata"""
    case_info: CaseInfo
    evidence_id: str
    examiner_name: str
    examiner_title: str
    examination_date: str
    methodology: str
    findings: str
    conclusions: str
    exhibits: List[Dict] = None
    chain_of_custody_file: str = ""
    hash_verification_file: str = ""


class ReportGenerator:
    """Generates forensic investigation reports"""
    
    def __init__(self, case_id: str, storage_dir: str = "evidence/reports"):
        """
        Initialize report generator
        
        Args:
            case_id: Case identifier
            storage_dir: Directory for storing reports
        """
        self.case_id = case_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_text_report(self, report: InvestigationReport) -> str:
        """
        Generate text format report
        
        Args:
            report: Investigation report data
            
        Returns:
            Formatted report as string
        """
        text_report = f"""
{'='*80}
DIGITAL FORENSIC INVESTIGATION REPORT
{'='*80}

TITLE PAGE
{'='*80}

Case ID:              {report.case_info.case_id}
Case Name:            {report.case_info.case_name}
Report Date:          {report.case_info.report_date}
Reporting Agency:     {report.case_info.reporting_agency}
Case Officer:         {report.case_info.case_officer}
Incident Date:        {report.case_info.incident_date}

Examiner Name:        {report.examiner_name}
Examiner Title:       {report.examiner_title}
Examination Date:     {report.examination_date}
Evidence ID:          {report.evidence_id}

{'='*80}

I. EXECUTIVE SUMMARY
{'='*80}

This report documents the digital forensic examination conducted on evidence
identified as {report.evidence_id} in connection with case {report.case_info.case_id}.
The examination was performed in accordance with ACPO (Association of Chief
Police Officers) guidelines for digital evidence preservation and analysis.

The examination was conducted to recover and analyze digital evidence related
to the investigation. This report provides a detailed account of the
examination procedures, findings, and conclusions.


II. INVESTIGATION SCOPE
{'='*80}

Evidence Examined:
  Evidence ID: {report.evidence_id}
  Examination Date: {report.examination_date}
  Examiner: {report.examiner_name}, {report.examiner_title}

Objectives:
  1. Acquire forensically sound image of evidence
  2. Verify integrity of acquired image
  3. Recover deleted or hidden files
  4. Analyze recovered data for relevant information
  5. Produce court-admissible report

Limitations:
  - Technical limitations of examination tools
  - Potential data corruption or degradation
  - Unallocated space may not be fully recoverable
  - File system overwriting may prevent recovery of older data


III. EVIDENCE DESCRIPTION
{'='*80}

Evidence details documented in chain of custody records.
See Appendix A for complete evidence information and photographs.


IV. CHAIN OF CUSTODY
{'='*80}

The chain of custody document demonstrates complete control and accountability
for the evidence throughout the investigation process.

Chain of Custody File: {report.chain_of_custody_file}

Summary:
  - Evidence properly sealed and stored
  - All access documented and tracked
  - Integrity verified through cryptographic hashing
  - No unauthorized access or modification

See Appendix B for complete chain of custody documentation.


V. EXAMINATION METHODOLOGY
{'='*80}

Equipment and Software:
  - Write-blocking device: Used to prevent data modification
  - Imaging software: ddrescue
  - Analysis tools: The Sleuth Kit, PhotoRec
  - Hash verification: MD5 and SHA-256

Procedures Followed:
{report.methodology}

ACPO Compliance:
  ✓ Principle 1: No action modified original data
  ✓ Principle 2: All personnel identified and qualified
  ✓ Principle 3: Procedures documented and standardized
  ✓ Principle 4: Senior examiner supervision and approval


VI. FINDINGS
{'='*80}

{report.findings}

See Appendix C for detailed technical findings.


VII. CONCLUSIONS
{'='*80}

{report.conclusions}

Files Recovered: [As documented in recovery reports]
Evidence Integrity: [VERIFIED/NOT VERIFIED]
Chain of Custody: [INTACT/BROKEN]


VIII. LIMITATIONS AND DISCLAIMERS
{'='*80}

This examination was performed using standard forensic procedures and tools.
The findings are based on the data available at the time of examination.
Conclusions are based on reasonable professional judgment.

Limitations:
  - Cannot recover data beyond memory/recovery limits of tools
  - File system fragmentation may prevent complete recovery
  - Some file types may not be identifiable
  - Encryption prevents analysis of encrypted data

Disclaimers:
  - This report is prepared for legal proceedings
  - Unauthorized reproduction or distribution is prohibited
  - Findings are subject to cross-examination and testing


{'='*80}
CERTIFICATION
{'='*80}

I hereby certify that:

1. I am competent to perform digital forensic examinations
2. The methods and procedures used are recognized in the field
3. The equipment was properly functioning and calibrated
4. The examination was conducted with scientific rigor
5. I have no bias or financial interest in the outcome
6. This report accurately reflects the findings of the examination
7. All work was performed under ACPO guidelines

Signature: _________________________

Printed Name: {report.examiner_name}

Title: {report.examiner_title}

Date: {report.examination_date}

License/Credential: _________________________


{'='*80}
APPENDICES
{'='*80}

Appendix A: Evidence Information and Photographs
  - Device specifications
  - Physical condition documentation
  - Serial numbers and identifiers

Appendix B: Chain of Custody Documentation
  - Full chain of custody record
  - Signatures and approvals
  - Storage and handling records
  - Verification dates and times

Appendix C: Technical Findings
  - File system analysis
  - Recovered file listings
  - File signatures and types
  - Data structure analysis
  - Unallocated space analysis

Appendix D: Hash Verification Report
  File: {report.hash_verification_file}
  
  Hash Verification Summary:
  - Original Image Hash
  - Verification Hash
  - Match Status: [VERIFIED]

Appendix E: Recovery Details
  - Files recovered by recovery method
  - File types identified
  - Recovery confidence levels
  - Timeline of file operations

Appendix F: Tool Documentation
  - Software versions and updates
  - Tool validation tests
  - Parameter settings
  - Known limitations

Appendix G: References and Standards
  - ACPO Good Practice Guide
  - NIST SP 800-86
  - ISO/IEC 27037:2012
  - ISO/IEC 27041:2015
  - ISO/IEC 27042:2015


{'='*80}
END OF REPORT
{'='*80}

Report Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
Document Classification: Confidential - Legal Discovery
"""
        
        return text_report
    
    def generate_html_report(self, report: InvestigationReport) -> str:
        """
        Generate HTML format report
        
        Args:
            report: Investigation report data
            
        Returns:
            HTML report as string
        """
        html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Forensic Investigation Report - {report.case_info.case_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            border-bottom: 3px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .case-info {{
            background-color: #f5f5f5;
            padding: 15px;
            margin-bottom: 30px;
            border-left: 4px solid #0066cc;
        }}
        .case-info p {{
            margin: 10px 0;
        }}
        section {{
            margin-bottom: 40px;
        }}
        section h2 {{
            background-color: #f9f9f9;
            padding: 10px 15px;
            border-left: 4px solid #0066cc;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .findings {{
            background-color: #fffbf0;
            padding: 15px;
            border-left: 4px solid #ff9800;
            margin: 15px 0;
        }}
        .certification {{
            border: 2px solid #000;
            padding: 20px;
            margin-top: 30px;
            background-color: #fafafa;
        }}
        .signature-line {{
            margin-top: 30px;
            border-top: 1px solid #000;
            width: 300px;
            height: 100px;
        }}
        footer {{
            border-top: 1px solid #ccc;
            margin-top: 50px;
            padding-top: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .toc {{
            background-color: #f5f5f5;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .toc ol {{
            column-count: 2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DIGITAL FORENSIC INVESTIGATION REPORT</h1>
        <p>ACPO Compliant - Court Admissible Evidence Documentation</p>
    </div>
    
    <div class="case-info">
        <h3>Case Information</h3>
        <p><strong>Case ID:</strong> {report.case_info.case_id}</p>
        <p><strong>Case Name:</strong> {report.case_info.case_name}</p>
        <p><strong>Reporting Agency:</strong> {report.case_info.reporting_agency}</p>
        <p><strong>Case Officer:</strong> {report.case_info.case_officer}</p>
        <p><strong>Incident Date:</strong> {report.case_info.incident_date}</p>
        <p><strong>Report Date:</strong> {report.case_info.report_date}</p>
        <hr>
        <p><strong>Examiner:</strong> {report.examiner_name}, {report.examiner_title}</p>
        <p><strong>Examination Date:</strong> {report.examination_date}</p>
        <p><strong>Evidence ID:</strong> {report.evidence_id}</p>
    </div>
    
    <section>
        <h2>Table of Contents</h2>
        <div class="toc">
            <ol>
                <li>Executive Summary</li>
                <li>Investigation Scope</li>
                <li>Evidence Description</li>
                <li>Chain of Custody</li>
                <li>Examination Methodology</li>
                <li>Findings</li>
                <li>Conclusions</li>
                <li>Limitations and Disclaimers</li>
                <li>Certification</li>
                <li>Appendices</li>
            </ol>
        </div>
    </section>
    
    <section>
        <h2>I. Executive Summary</h2>
        <p>This report documents the digital forensic examination conducted on evidence
        identified as {report.evidence_id} in connection with case {report.case_info.case_id}.
        The examination was performed in accordance with ACPO guidelines.</p>
    </section>
    
    <section>
        <h2>II. Investigation Scope</h2>
        <p>The examination was conducted to recover and analyze digital evidence related
        to the investigation.</p>
        <h3>Objectives:</h3>
        <ul>
            <li>Acquire forensically sound image of evidence</li>
            <li>Verify integrity of acquired image</li>
            <li>Recover deleted or hidden files</li>
            <li>Analyze recovered data for relevant information</li>
            <li>Produce court-admissible report</li>
        </ul>
    </section>
    
    <section>
        <h2>III. Examination Methodology</h2>
        <h3>ACPO Compliance:</h3>
        <ul>
            <li>✓ Principle 1: No action modified original data</li>
            <li>✓ Principle 2: All personnel identified and qualified</li>
            <li>✓ Principle 3: Procedures documented and standardized</li>
            <li>✓ Principle 4: Senior examiner supervision and approval</li>
        </ul>
        <p>{report.methodology}</p>
    </section>
    
    <section>
        <h2>IV. Findings</h2>
        <div class="findings">
            {report.findings}
        </div>
    </section>
    
    <section>
        <h2>V. Conclusions</h2>
        <p>{report.conclusions}</p>
    </section>
    
    <section class="certification">
        <h2>VI. Certification</h2>
        <p>I hereby certify that:</p>
        <ol>
            <li>I am competent to perform digital forensic examinations</li>
            <li>The methods and procedures used are recognized in the field</li>
            <li>The equipment was properly functioning and calibrated</li>
            <li>The examination was conducted with scientific rigor</li>
            <li>I have no bias or financial interest in the outcome</li>
            <li>This report accurately reflects the findings of the examination</li>
            <li>All work was performed under ACPO guidelines</li>
        </ol>
        
        <div class="signature-line"></div>
        <p><strong>{report.examiner_name}</strong><br>
        {report.examiner_title}<br>
        Date: {report.examination_date}</p>
    </section>
    
    <footer>
        <p>This report is confidential and intended for legal discovery purposes only.</p>
        <p>Unauthorized reproduction or distribution is prohibited.</p>
        <p>Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
    </footer>
</body>
</html>
"""
        
        return html_report
    
    def save_report(
        self,
        report: InvestigationReport,
        format: str = "text"
    ) -> str:
        """
        Save report to file
        
        Args:
            report: Investigation report data
            format: Report format (text, html, json)
            
        Returns:
            Path to saved report
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "text":
            content = self.generate_text_report(report)
            filename = f"{report.evidence_id}_report_{timestamp}.txt"
        elif format.lower() == "html":
            content = self.generate_html_report(report)
            filename = f"{report.evidence_id}_report_{timestamp}.html"
        elif format.lower() == "json":
            content = json.dumps({
                "case_info": {
                    "case_id": report.case_info.case_id,
                    "case_name": report.case_info.case_name,
                    "report_date": report.case_info.report_date,
                },
                "evidence_id": report.evidence_id,
                "examiner": report.examiner_name,
                "examination_date": report.examination_date,
                "findings": report.findings,
                "conclusions": report.conclusions
            }, indent=2)
            filename = f"{report.evidence_id}_report_{timestamp}.json"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        output_path = self.storage_dir / filename
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"Report saved: {output_path}")
        return str(output_path)


# Example usage
if __name__ == "__main__":
    generator = ReportGenerator("CASE_2026_001")
    
    case_info = CaseInfo(
        case_id="THEFT_2026_000001",
        case_name="Alleged Computer Theft - ABC Corp",
        reporting_agency="Metropolitan Police Department",
        case_officer="Detective Jane Smith",
        incident_date="2026-03-15",
        report_date="2026-04-03"
    )
    
    report = InvestigationReport(
        case_info=case_info,
        evidence_id="THEFT_2026_000001_001",
        examiner_name="John Doe",
        examiner_title="Senior Forensic Examiner",
        examination_date="2026-04-01",
        methodology="Forensic imaging using ddrescue with write-blocking device.",
        findings="250 JPEG files recovered from unallocated space.",
        conclusions="Data consistent with user activity on the evidence device.",
        chain_of_custody_file="evidence/cases/THEFT_2026_000001_001_coc.json",
        hash_verification_file="evidence/cases/THEFT_2026_000001_hashes.json"
    )
    
    # Generate reports
    text_report_path = generator.save_report(report, format="text")
    html_report_path = generator.save_report(report, format="html")
    json_report_path = generator.save_report(report, format="json")
    
    print(f"Text Report: {text_report_path}")
    print(f"HTML Report: {html_report_path}")
    print(f"JSON Report: {json_report_path}")
