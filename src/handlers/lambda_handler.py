from aws_python_helper.lambda_standalone.handler import lambda_handler

scrape_tax_sales_handler = lambda_handler("scrape-tax-sales")

__all__ = ["scrape_tax_sales_handler"]
