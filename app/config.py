import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    #DB_FILE = '/app/db/charts.db'
    DB_FILE = '/home/omerkhan/charting_engine/database/charts.db'
    DATA_API_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiUkFQSURfQVBJX1VTRVIiLCJDb21wYW55SUQiOiI3NyIsIk1hcmtldElEIjoiMyIsIkZTQW5udWFsIjoiMTAwIiwiRlNRdWFydGVyIjoiMjAwIiwiRlNJbnRlcm0iOiIxMDAiLCJGUkFubnVhbCI6IjEwMCIsIkZSUXVhcnRlciI6IjIwMCIsIkZSSW50ZXJtIjoiMTAwIiwiRmluYW5jaWFsSGlnaGxpZ2h0cyI6IlRydWUiLCJTaGFyZWhvbGRlcnNIaXN0b3J5IjoiVHJ1ZSIsIm5iZiI6MTY3NjM3MzQ0NywiZXhwIjoxNjg3MTczNDQ3LCJpYXQiOjE2NzYzNzM0NDd9.o2_WGBQ8Ujh3ChkCV0iitFYQjaIhQJjv_Sh5CicFfaE'
    DATA_API_URL = 'https://data.edanat.com'