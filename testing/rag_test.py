#!/usr/bin/env python3
"""
RAG Test Script for Linebot_healmate

This script tests the RAG functionality by querying the RAG service
with sample queries and displaying the results.
"""

import asyncio
import os
import sys
import logging
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add project root to path to import services
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Import the RAG service
from services.rag import rag_service

# Create rich console for nice output
console = Console()

async def test_rag_queries(queries: List[str]) -> None:
    """
    Test the RAG service with a list of queries.
    
    Args:
        queries: List of text queries to test
    """
    # Initialize collection if needed
    rag_service.create_collection_if_not_exists()
    
    console.print("\n[bold green]Testing RAG Queries[/bold green]")
    
    for query in queries:
        console.print(f"\n[bold blue]Query:[/bold blue] {query}")
        
        try:
            # Get query results
            results = await rag_service.query(
                text=query,
                limit=5
            )
            
            if results:
                # Display results in a table
                table = Table(title=f"Results for: '{query}'")
                table.add_column("Score", justify="right", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Content", style="white")
                
                for result in results:
                    table.add_row(
                        str(result.get("score", "N/A")),
                        result.get("title", "Untitled"),
                        result.get("content", "No content")[:100] + "..." if len(result.get("content", "")) > 100 else result.get("content", "No content")
                    )
                
                console.print(table)
                console.print(f"Found [bold green]{len(results)}[/bold green] results")
            else:
                console.print("[yellow]No results found for this query.[/yellow]")
                console.print("\nThis could indicate that:")
                console.print("1. The collection is empty (needs data ingestion)")
                console.print("2. The query has no relevant matches")
                console.print("3. The similarity threshold is too high")
        
        except Exception as e:
            console.print(f"[bold red]Error querying RAG service:[/bold red] {str(e)}")

async def check_collection_status() -> None:
    """Check if the RAG collection has any documents."""
    try:
        # This is a basic test to see if we get any results
        test_results = await rag_service.query(
            text="test query to check collection status",
            limit=1
        )
        
        if test_results:
            console.print(f"\n[bold green]Collection '{rag_service.COLLECTION_NAME}' contains documents.[/bold green]")
        else:
            console.print(f"\n[bold yellow]Warning: Collection '{rag_service.COLLECTION_NAME}' appears to be empty.[/bold yellow]")
            console.print("You need to add documents to the collection before RAG will be effective.")
    except Exception as e:
        console.print(f"[bold red]Error checking collection status:[/bold red] {str(e)}")

async def main() -> None:
    """Run RAG tests."""
    console.print("[bold]RAG Test for Linebot_healmate[/bold]")
    console.print(f"Using collection: [cyan]{rag_service.COLLECTION_NAME}[/cyan]")
    console.print(f"Embedding model: [cyan]{'Ollama/' + rag_service.OLLAMA_MODEL if rag_service.OLLAMA_ENABLED else 'OpenAI/' + rag_service.OPENAI_EMBEDDING_MODEL}[/cyan]")
    
    # Check if collection has documents
    await check_collection_status()
    
    # Test queries
    test_queries = [
        "What is the meaning of the death card?",
        "What does the fool represent in tarot?",
        "How to interpret the tower card?",
        "Tell me about the cups suit in tarot",
        "What is a card reading spread?"
    ]
    
    await test_rag_queries(test_queries)

if __name__ == "__main__":
    asyncio.run(main())
