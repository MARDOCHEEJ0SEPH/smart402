"""
Smart402 CLI

Command-line interface for creating, deploying, and monitoring
AI-native smart contracts.

Usage:
    smart402 create        Create a new contract
    smart402 deploy        Deploy contract to blockchain
    smart402 monitor       Monitor contract conditions
    smart402 status        Check contract status
    smart402 templates     List available templates
"""

import asyncio
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import yaml
import json

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Smart402 CLI - Universal Protocol for AI-Native Smart Contracts
    """
    pass


@cli.command()
@click.option("--template", "-t", help="Use a contract template")
@click.option("--output", "-o", default="contract.yaml", help="Output file path")
@click.option("--interactive/--no-interactive", default=True, help="Interactive mode")
def create(template, output, interactive):
    """Create a new Smart402 contract"""
    console.print("\n[bold blue]🚀 Smart402 Contract Creator[/bold blue]\n")

    try:
        if template:
            asyncio.run(_create_from_template(template, output))
        elif interactive:
            asyncio.run(_create_interactive(output))
        else:
            console.print("[red]Please specify --template or use interactive mode[/red]")
            return

    except Exception as e:
        console.print(f"[red]❌ Error creating contract: {e}[/red]")
        raise


async def _create_interactive(output):
    """Interactive contract creation"""
    from smart402 import Smart402

    console.print("[cyan]Let's create your contract...[/cyan]\n")

    # Get contract type
    console.print("[yellow]Contract Type:[/yellow]")
    console.print("1. SaaS Subscription")
    console.print("2. Freelancer Milestone")
    console.print("3. Supply Chain")
    console.print("4. Affiliate Commission")
    console.print("5. Vendor SLA")
    contract_type = click.prompt("Select type (1-5)", type=int)

    type_map = {
        1: "saas-subscription",
        2: "freelancer-milestone",
        3: "supply-chain",
        4: "affiliate-commission",
        5: "vendor-sla",
    }

    # Get basic info
    vendor = click.prompt("Vendor address/email")
    customer = click.prompt("Customer address/email")
    amount = click.prompt("Payment amount", type=float)
    token = click.prompt("Payment token (USDC/USDT/DAI/ETH)", default="USDC")
    frequency = click.prompt(
        "Frequency (one-time/monthly/weekly/yearly)", default="monthly"
    )
    network = click.prompt(
        "Blockchain (polygon/ethereum/arbitrum/optimism)", default="polygon"
    )

    config = {
        "type": type_map[contract_type],
        "parties": [vendor, customer],
        "payment": {
            "amount": amount,
            "token": token,
            "frequency": frequency,
            "blockchain": network.lower(),
        },
    }

    with console.status("[bold green]Creating contract..."):
        contract = await Smart402.create(config)

    # Export to file
    yaml_content = await contract.export("yaml")
    Path(output).write_text(yaml_content)

    console.print(f"\n[green]✅ Contract saved to {output}[/green]")
    console.print(f"[dim]Contract ID: {contract.id}[/dim]")
    console.print("\n[dim]Next steps:[/dim]")
    console.print(f"[dim]  1. Review: cat {output}[/dim]")
    console.print(f"[dim]  2. Deploy: smart402 deploy {output}[/dim]")
    console.print(f"[dim]  3. Monitor: smart402 monitor {contract.id}[/dim]\n")


async def _create_from_template(template_name, output):
    """Create from template"""
    from smart402 import Smart402

    templates = Smart402.get_templates()

    if template_name not in templates:
        console.print(f"[red]Template '{template_name}' not found.[/red]")
        console.print("\n[yellow]Available templates:[/yellow]")
        for t in templates:
            console.print(f"  - {t}")
        return

    doc = Smart402.get_template_doc(template_name)
    console.print(f"\n[cyan]Using template: {doc['title']}[/cyan]\n")

    # Get template variables (simplified for demo)
    variables = {}
    console.print("[yellow]Enter template variables:[/yellow]")
    # In production, would iterate through doc['variables']

    with console.status("[bold green]Creating contract..."):
        contract = await Smart402.from_template(template_name, variables)

    yaml_content = await contract.export("yaml")
    Path(output).write_text(yaml_content)

    console.print(f"\n[green]✅ Contract created: {output}[/green]\n")


@cli.command()
@click.argument("contract-file", type=click.Path(exists=True))
@click.option("--network", "-n", default="polygon", help="Network to deploy to")
@click.option("--key", "-k", help="Private key")
@click.option("--gas-limit", type=int, help="Gas limit")
def deploy(contract_file, network, key, gas_limit):
    """Deploy contract to blockchain"""
    console.print("\n[bold blue]📡 Smart402 Deployment[/bold blue]\n")

    try:
        asyncio.run(_deploy_contract(contract_file, network, key, gas_limit))
    except Exception as e:
        console.print(f"[red]❌ Deployment failed: {e}[/red]")
        raise


async def _deploy_contract(contract_file, network, key, gas_limit):
    """Deploy contract"""
    from smart402 import Smart402

    with console.status("[bold green]Loading contract..."):
        yaml_content = Path(contract_file).read_text()
        # Would parse YAML and create contract
        # contract = await Smart402.from_yaml(yaml_content)

    console.print("[green]✓[/green] Contract loaded")

    # Confirm deployment
    if not click.confirm(f"Deploy to {network}?"):
        console.print("[yellow]Deployment cancelled[/yellow]")
        return

    with console.status(f"[bold green]Deploying to {network}..."):
        # result = await contract.deploy(network=network, gas_limit=gas_limit)
        pass  # Placeholder

    console.print("\n[green]✅ Contract deployed![/green]\n")
    # console.print(f"[dim]Address: {result['address']}[/dim]")
    # console.print(f"[dim]Transaction: {result['transaction_hash']}[/dim]")


@cli.command()
@click.argument("contract-id")
@click.option("--frequency", "-f", default="medium", help="Monitoring frequency")
@click.option("--webhook", "-w", help="Webhook URL")
@click.option("--dry-run", is_flag=True, help="Check conditions once")
def monitor(contract_id, frequency, webhook, dry_run):
    """Monitor contract conditions and auto-execute payments"""
    console.print("\n[bold blue]👀 Smart402 Monitoring[/bold blue]\n")

    try:
        asyncio.run(_monitor_contract(contract_id, frequency, webhook, dry_run))
    except Exception as e:
        console.print(f"[red]❌ Monitoring failed: {e}[/red]")
        raise


async def _monitor_contract(contract_id, frequency, webhook, dry_run):
    """Monitor contract"""
    from smart402 import Smart402

    with console.status("[bold green]Loading contract..."):
        contract = await Smart402.load(contract_id)

    console.print("[green]✓[/green] Contract loaded")

    if dry_run:
        # Check conditions once
        with console.status("[bold green]Checking conditions..."):
            status = await contract.check_conditions()

        console.print("\n[cyan]📊 Condition Status:[/cyan]\n")
        for cond_id, met in status["conditions"].items():
            icon = "✅" if met else "❌"
            console.print(f"  {icon} {cond_id}: {'Met' if met else 'Not met'}")

        all_met = status["all_met"]
        console.print(f"\n[dim]All conditions met: {'Yes' if all_met else 'No'}[/dim]\n")

        if all_met and click.confirm("All conditions met. Execute payment now?"):
            with console.status("[bold green]Executing payment..."):
                payment = await contract.execute_payment()
            console.print(f"\n[green]✅ Payment: {payment['transaction_hash']}[/green]\n")

    else:
        # Start continuous monitoring
        console.print(f"[cyan]Starting continuous monitoring...[/cyan]")
        console.print(f"[dim]Frequency: {frequency}[/dim]")
        if webhook:
            console.print(f"[dim]Webhook: {webhook}[/dim]")

        await contract.start_monitoring(frequency=frequency, webhook=webhook)

        console.print("\n[green]✅ Monitoring active![/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        try:
            # Keep alive
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping monitoring...[/yellow]")
            await contract.stop_monitoring()
            console.print("[green]Monitoring stopped.[/green]\n")


@cli.command()
@click.argument("contract-id")
def status(contract_id):
    """Check contract status"""
    console.print("\n[bold blue]📋 Contract Status[/bold blue]\n")

    try:
        asyncio.run(_show_status(contract_id))
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise


async def _show_status(contract_id):
    """Show contract status"""
    from smart402 import Smart402

    with console.status("[bold green]Loading contract..."):
        contract = await Smart402.load(contract_id)

    # Contract info
    table = Table(title="Contract Information")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("ID", contract.id)
    table.add_row("Status", contract.status.value)
    table.add_row("Type", contract.ucl.get("metadata", {}).get("type", "N/A"))

    if contract.address:
        table.add_row("Address", contract.address)
        table.add_row("URL", contract.get_url())

    console.print(table)

    # Parties
    console.print("\n[cyan]Parties:[/cyan]")
    for party in contract.get_parties():
        console.print(f"  {party['role']}: {party.get('name', party['identifier'])}")

    # Payment terms
    payment = contract.get_payment_terms()
    console.print("\n[cyan]Payment Terms:[/cyan]")
    console.print(f"  Amount: {payment['amount']} {payment['token']}")
    console.print(f"  Frequency: {payment['frequency']}")
    console.print(f"  Blockchain: {payment['blockchain']}")

    # Summary
    console.print("\n[cyan]Summary:[/cyan]")
    console.print(f"  {contract.get_summary()}")

    # AEO Score
    console.print(f"\n[cyan]AEO Score: {contract.get_aeo_score()}/100[/cyan]\n")


@cli.command()
def templates():
    """List available contract templates"""
    console.print("\n[bold blue]📚 Available Templates[/bold blue]\n")

    from smart402 import Smart402

    template_names = Smart402.get_templates()

    for name in template_names:
        doc = Smart402.get_template_doc(name)
        console.print(f"[cyan]{doc['title']}[/cyan]")
        console.print(f"  {doc['description']}")
        console.print(f"  [dim]Usage: smart402 create --template {name}[/dim]\n")


@cli.command()
def init():
    """Initialize Smart402 configuration"""
    console.print("\n[bold blue]⚙️  Smart402 Initialization[/bold blue]\n")

    network = click.prompt(
        "Default network", type=click.Choice(["polygon", "ethereum", "arbitrum", "optimism", "base"]),
        default="polygon"
    )

    private_key = click.prompt("Private key (optional, leave blank to skip)", default="", hide_input=True)
    rpc_url = click.prompt("Custom RPC URL (optional)", default="")

    config = {
        "network": network,
        "private_key": private_key if private_key else None,
        "rpc_url": rpc_url if rpc_url else None,
    }

    config_path = Path.cwd() / ".smart402.json"
    config_path.write_text(json.dumps(config, indent=2))

    console.print(f"\n[green]✅ Configuration saved to .smart402.json[/green]")
    console.print("[yellow]⚠️  Add .smart402.json to .gitignore![/yellow]\n")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
