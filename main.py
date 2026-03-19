"""
Main entry point for KYC/AML Multi-Agent System
"""
import sys
import json
import argparse
from pathlib import Path
from loguru import logger
from orchestrator import KYCOrchestrator


def setup_logging():
    """Configure logging"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/kyc_system_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )


def load_document(document_path: str) -> dict:
    """Load document from file"""
    try:
        with open(document_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load document: {str(e)}")
        sys.exit(1)


def print_results(result: dict):
    """Print results in a formatted way"""
    print("\n" + "=" * 80)
    print("KYC/AML PROCESSING COMPLETE")
    print("=" * 80)
    
    print(f"\n{'DECISION:':<20} {result['decision']}")
    print(f"{'Risk Category:':<20} {result['risk_category']}")
    print(f"{'Risk Score:':<20} {result['risk_score']:.2f}")
    print(f"{'Confidence:':<20} {result['confidence']:.2f}")
    print(f"{'Recommendation:':<20} {result['recommendation']}")
    
    print(f"\n{'Applicant:':<20} {result.get('extracted_data', {}).get('name', 'N/A')}")
    print(f"{'ID Number:':<20} {result.get('extracted_data', {}).get('id_number', 'N/A')}")
    print(f"{'DOB:':<20} {result.get('extracted_data', {}).get('date_of_birth', 'N/A')}")
    
    print("\nEXPLANATION:")
    print("-" * 80)
    print(result.get('explanation', 'No explanation available'))
    
    print("\n" + "=" * 80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='KYC/AML Multi-Agent System')
    parser.add_argument(
        '--document',
        type=str,
        help='Path to document JSON file',
        default='samples/pan_card.json'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output JSON file (optional)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode to select document'
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_logging()
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("Initializing KYC/AML Multi-Agent System")
    
    # Interactive mode
    if args.interactive:
        print("\nAvailable sample documents:")
        samples = list(Path("samples").glob("*.json"))
        for i, sample in enumerate(samples, 1):
            print(f"{i}. {sample.name}")
        
        choice = input("\nSelect document number: ")
        try:
            args.document = str(samples[int(choice) - 1])
        except (ValueError, IndexError):
            print("Invalid selection")
            sys.exit(1)
    
    # Load document
    logger.info(f"Loading document: {args.document}")
    document = load_document(args.document)
    
    # Process document
    orchestrator = KYCOrchestrator()
    result = orchestrator.process_document(document)
    
    # Print results
    print_results(result)
    
    # Save output if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results saved to {args.output}")
    
    logger.info("Processing complete")
    
    return 0 if result['decision'] != 'ERROR' else 1


if __name__ == "__main__":
    sys.exit(main())