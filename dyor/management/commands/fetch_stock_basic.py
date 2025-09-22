"""
Django Management Command: fetch_stock_basic

This command fetches stock basic information from Tushare Pro API and creates/updates
EqBasic records in the database.

Usage Examples:
    # Fetch all listed stocks to default database
    python manage.py fetch_stock_basic

    # Fetch stocks from specific exchange
    python manage.py fetch_stock_basic --exchange SSE

    # Use different database
    python manage.py fetch_stock_basic --database digitalocean

    # Fetch only specific fields
    python manage.py fetch_stock_basic --fields ts_code symbol name industry

    # Dry run to see what would be processed
    python manage.py fetch_stock_basic --dry-run

    # Fetch delisted stocks
    python manage.py fetch_stock_basic --list-status D

Requirements:
    - TUSHARE_TOKEN environment variable must be set
    - Valid database configuration in settings.py
    - Internet connection for API calls

API Reference: https://tushare.pro/document/2?doc_id=25
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.dateparse import parse_date

from dyor.dao import eq_basic_dao
from dyor.tushare.client import TushareClient


class Command(BaseCommand):
    help = "Fetch stock basic information from Tushare and create/update EqBasic records"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--database",
            type=str,
            default="default",
            help="Database to use for operations (default: 'default')",
        )
        parser.add_argument(
            "--exchange",
            type=str,
            default="",
            help="Exchange filter (SSE/SZSE/BSE, empty for all)",
        )
        parser.add_argument(
            "--list-status",
            type=str,
            default="L",
            choices=["L", "D", "P"],
            help="Listing status filter: L=Listed, D=Delisted, P=Suspended (default: L)",
        )
        parser.add_argument(
            "--fields",
            type=str,
            nargs="*",
            help="Specific fields to fetch (if not provided, fetches all available fields)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Batch size for processing records (default: 1000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making database changes",
        )

    def handle(self, *args, **options):
        # Validate database option
        database = options["database"]
        if database not in ["default", "digitalocean"]:
            raise CommandError(f"Invalid database option: {database}")
        
        # Database parameter is now fully supported by DAO layer

        # Get Tushare token
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            raise CommandError("TUSHARE_TOKEN environment variable not found")

        # Initialize Tushare client
        try:
            client = TushareClient(token=token, base_url="http://api.tushare.pro")
        except Exception as e:
            raise CommandError(f"Failed to initialize Tushare client: {e}")

        # Prepare API parameters
        params = {
            "list_status": options["list_status"],
        }
        if options["exchange"]:
            params["exchange"] = options["exchange"]

        # Define all available fields from the API
        all_fields = [
            "ts_code",
            "symbol", 
            "name",
            "area",
            "industry",
            "fullname",
            "enname",
            "cnspell",
            "market",
            "exchange",
            "curr_type",
            "list_status",
            "list_date",
            "delist_date",
            "is_hs",
            "act_name",
            "act_ent_type",
        ]

        # Use specified fields or all fields
        fields = options["fields"] if options["fields"] else all_fields

        self.stdout.write(
            self.style.SUCCESS(
                f"Fetching stock basic data from Tushare..."
                f"\nDatabase: {database}"
                f"\nExchange: {options['exchange'] or 'All'}"
                f"\nList Status: {options['list_status']}"
                f"\nFields: {', '.join(fields)}"
                f"\nDry Run: {options['dry_run']}"
            )
        )

        try:
            # Fetch data from Tushare
            self.stdout.write("Calling Tushare stock_basic API...")
            result = client.stock_basic(params=params, fields=fields)
            
            if not result:
                self.stdout.write(self.style.WARNING("No data returned from Tushare API"))
                return

            # Handle different response formats
            if isinstance(result, dict):
                # Extract fields and items from response
                response_fields = result.get("fields", fields)  # Use response fields if available
                items = result.get("items", [])
            elif isinstance(result, list):
                # If it's just a list, assume it matches the requested fields
                response_fields = fields
                items = result
            else:
                self.stdout.write(self.style.WARNING("Unexpected response format from Tushare API"))
                return

            self.stdout.write(f"Retrieved {len(items)} records from Tushare")
            self.stdout.write(f"Response fields: {response_fields}")

            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("DRY RUN: No database changes will be made"))
                self._display_sample_data(items[:5], response_fields)
                return

            # Process records in batches
            batch_size = options["batch_size"]
            created_count = 0
            updated_count = 0
            error_count = 0

            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_created, batch_updated, batch_errors = self._process_batch(
                    batch, database, response_fields
                )
                created_count += batch_created
                updated_count += batch_updated
                error_count += batch_errors

                self.stdout.write(
                    f"Processed batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}: "
                    f"{batch_created} created, {batch_updated} updated, {batch_errors} errors"
                )

            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nProcessing completed successfully!"
                    f"\nTotal records processed: {len(items)}"
                    f"\nCreated: {created_count}"
                    f"\nUpdated: {updated_count}"
                    f"\nErrors: {error_count}"
                )
            )

        except Exception as e:
            raise CommandError(f"Error fetching or processing data: {e}")

    def _process_batch(
        self, batch: List[Dict], database: str, fields: List[str]
    ) -> tuple[int, int, int]:
        """Process a batch of records using DAO"""
        created_count = 0
        updated_count = 0
        error_count = 0

        try:
            # Map all items to model fields
            mapped_data_list = []
            for item in batch:
                try:
                    mapped_data = self._map_tushare_to_model(item, fields)
                    if mapped_data.get("ticker"):  # Only process if ticker exists
                        mapped_data_list.append(mapped_data)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error mapping record {item.get('ts_code', 'unknown')}: {e}")
                    )
                    error_count += 1

            if not mapped_data_list:
                return created_count, updated_count, error_count

            # Use DAO methods for each record with database routing
            for mapped_data in mapped_data_list:
                try:
                    ticker = mapped_data["ticker"]
                    
                    # Check if record exists first
                    existing_record = eq_basic_dao.get_by_ticker(ticker, using=database)
                    
                    if existing_record:
                        # Update existing record
                        eq_basic_dao.update(existing_record, using=database, **{k: v for k, v in mapped_data.items() if k != "ticker"})
                        updated_count += 1
                    else:
                        # Create new record
                        eq_basic_dao.create(using=database, **mapped_data)
                        created_count += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing record {mapped_data.get('ticker', 'unknown')}: {e}")
                    )
                    error_count += 1

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error processing batch: {e}")
            )
            error_count += len(batch)

        return created_count, updated_count, error_count

    def _map_tushare_to_model(self, item, fields: List[str]) -> Dict:
        """Map Tushare API response to model fields"""
        mapped_data = {}
        
        # Field mapping from Tushare to model
        field_mapping = {
            "ts_code": "ticker",
            "symbol": "code",
            "name": "name",
            "area": "area",
            "industry": "industry",
            "fullname": "fullname",
            "enname": "enname",
            "cnspell": "cnspell",
            "market": "market",
            "exchange": "exchange",
            "curr_type": "curr_type",
            "list_status": "list_status",
            "list_date": "list_date",
            "delist_date": "delist_date",
            "is_hs": "is_hs",
            "act_name": "act_name",
            "act_ent_type": "act_ent_type",
        }

        for i, tushare_field in enumerate(fields):
            if tushare_field in field_mapping:
                model_field = field_mapping[tushare_field]
                
                # Handle different data formats
                if isinstance(item, dict):
                    value = item.get(tushare_field)
                elif isinstance(item, list) and i < len(item):
                    value = item[i]
                else:
                    value = None
                
                # Handle date fields
                if model_field in ["list_date", "delist_date"] and value:
                    try:
                        # Tushare returns dates as YYYYMMDD strings
                        if len(str(value)) == 8:
                            value = datetime.strptime(str(value), "%Y%m%d").date()
                        else:
                            value = parse_date(str(value))
                    except (ValueError, TypeError):
                        value = None
                
                # Handle empty strings as None
                if value == "":
                    value = None
                    
                mapped_data[model_field] = value

        return mapped_data

    def _display_sample_data(self, items: List, response_fields: List[str]):
        """Display sample data for dry run"""
        self.stdout.write("\nSample data that would be processed:")
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                # Handle dictionary format
                self.stdout.write(f"\n{i}. {item.get('ts_code', 'N/A')} - {item.get('name', 'N/A')}")
                for key, value in item.items():
                    if value:  # Only show non-empty values
                        self.stdout.write(f"   {key}: {value}")
            elif isinstance(item, list):
                # Handle list format (assuming fields are in the same order as requested)
                # This part needs to be careful as list items might not directly map to response_fields
                # For simplicity, we'll just print the list item and its index
                self.stdout.write(f"\n{i}. {item[0] if len(item) > 0 else 'N/A'} - {item[2] if len(item) > 2 else 'N/A'}")
                for j, value in enumerate(item):
                    if value:  # Only show non-empty values
                        self.stdout.write(f"   Field {j}: {value}")
            else:
                self.stdout.write(f"\n{i}. {item}")
