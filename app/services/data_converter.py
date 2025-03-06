import os
import json
import xmltodict
import pandas as pd
import logging
from flask import current_app
from app.services.file_handler import FileHandler
from app.models.user import User, db
from app.models.conversion_log import ConversionLog

class DataConverterService:
    def __init__(self):
        self._file_handler = None
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @property
    def file_handler(self):
        if self._file_handler is None:
            self._file_handler = FileHandler()
        return self._file_handler

    def convert_file(self, file, user_id):
        try:
            file_info = self.file_handler.save_file(file)
            conversion_methods = {'json': self._convert_json, 'xml': self._convert_xml}
            converter = conversion_methods.get(file_info['file_extension'])
            if not converter:
                raise ValueError(f"Unsupported file type: {file_info['file_extension']}")
            conversion_result = converter(file_info['filepath'])
            return {'original_file': file_info, 'conversion_result': conversion_result}
        except Exception as e:
            self.logger.error(f"Conversion error: {str(e)}")
            raise ValueError(f"Conversion failed: {str(e)}")
    
    def _convert_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.json_normalize(data, sep='_')
                base_path = filepath.rsplit('.', 1)[0]
                csv_output = f"{base_path}_converted.csv"
                excel_output = f"{base_path}_converted.xlsx"
                df.to_csv(csv_output, index=False, encoding='utf-8')
                df.to_excel(excel_output, index=False)
                return {'csv_path': csv_output, 'excel_path': excel_output, 'total_rows': len(df), 'total_columns': len(df.columns)}
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            self.logger.error(f"JSON conversion error: {str(e)}")
            raise ValueError(f"JSON conversion failed: {str(e)}")
    
    def _convert_xml(self, filepath):
        """
        Convert XML file to CSV and Excel with improved flattening
        
        Args:
            filepath (str): Path to the XML file
        
        Returns:
            dict: Paths of converted files
        """
        try:
            # Read XML file
            with open(filepath, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Parse XML to dict
            parsed_data = xmltodict.parse(xml_content)
            
            # Find the root element and get the list of records
            # Assuming structure like <RootElement><Record>...</Record><Record>...</Record></RootElement>
            root_key = list(parsed_data.keys())[0]
            records = []
            
            # Handle different possible structures
            if isinstance(parsed_data[root_key], dict):
                # Find child elements that are lists
                for key, value in parsed_data[root_key].items():
                    if isinstance(value, list):
                        # Found a list of records
                        records = value
                        break
                
                # If no list found, maybe there's only one record or we need to search deeper
                if not records:
                    # Check if the root itself is a container for a single record
                    records = [parsed_data[root_key]]
            elif isinstance(parsed_data[root_key], list):
                # Root directly contains a list of records
                records = parsed_data[root_key]
            
            # Process each record into a flat dictionary
            flattened_records = []
            for record in records:
                flat_record = {}
                
                def flatten_element(element, prefix=""):
                    if isinstance(element, dict):
                        for k, v in element.items():
                            # Handle special case for attributes and text content
                            if k.startswith('@'):
                                # This is an attribute
                                attr_name = k[1:]  # Remove the @ symbol
                                flatten_element({attr_name: v}, prefix)
                            elif k == '#text':
                                # This is text content of an element with attributes
                                if prefix:
                                    # Use the parent element name
                                    flat_record[prefix.rstrip('.')] = v
                            else:
                                # Regular nested element
                                new_prefix = f"{prefix}{k}." if prefix else f"{k}."
                                flatten_element(v, new_prefix)
                    elif isinstance(element, list):
                        # Handle lists by creating indexed entries
                        for i, item in enumerate(element):
                            item_prefix = f"{prefix}[{i}]"
                            if isinstance(item, (dict, list)):
                                flatten_element(item, item_prefix + ".")
                            else:
                                flat_record[item_prefix] = item
                    else:
                        # Simple value
                        if prefix:
                            flat_record[prefix.rstrip('.')] = element
                        else:
                            flat_record["value"] = element
                
                flatten_element(record)
                flattened_records.append(flat_record)
            
            # Convert to DataFrame
            df = pd.DataFrame(flattened_records)
            
            # Generate output filenames
            base_path = filepath.rsplit('.', 1)[0]
            csv_output = f"{base_path}_converted.csv"
            excel_output = f"{base_path}_converted.xlsx"
            
            # Save conversions
            df.to_csv(csv_output, index=False, encoding='utf-8')
            df.to_excel(excel_output, index=False)
            
            return {
                'csv_path': csv_output,
                'excel_path': excel_output,
                'total_rows': len(df),
                'total_columns': len(df.columns)
            }
        
        except Exception as e:
            self.logger.error(f"XML conversion error: {str(e)}")
            raise ValueError(f"XML conversion failed: {str(e)}")
