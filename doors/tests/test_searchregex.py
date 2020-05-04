"""
A utility to ensure search parsing is working correctly
"""
## Target
from .. import search
from ..search import SearchField as SF
## Test Framwork
from django import test
## This module
from .. import models

TESTS = [
    ## ( input , result ),
    ################# BASE
    ("test", [SF(None,None,"test",False),] ),
    ("-test", [SF(None,None,"test",True),] ),
    ('"foo bar"', [SF(None,None,'"foo bar"',False),] ),
    ('-"foo bar"', [SF(None,None,'"foo bar"',True),] ),
    ################# Order->Text Search
    ("customer:test", [SF(models.Order,"customer","test",False),] ),
    ("-customer:test", [SF(models.Order,"customer","test",True),] ),
    ('customer:"test"', [SF(models.Order,"customer",'"test"',False),] ),
    ("customer_po:test", [SF(models.Order,"customer_po","test",False),] ),
    ("-customer_po:test", [SF(models.Order,"customer_po","test",True),] ),
    ('customer_po:"test"', [SF(models.Order,"customer_po",'"test"',False),] ),
    ("po:test", [SF(models.Order,"customer_po","test",False),] ),
    ("-po:test", [SF(models.Order,"customer_po","test",True),] ),
    ('po:"test"', [SF(models.Order,"customer_po",'"test"',False),] ),
    ("work_order:test", [SF(models.Order,"work_order","test",False),] ),
    ("-work_order:test", [SF(models.Order,"work_order","test",True),] ),
    ('work_order:"test"', [SF(models.Order,"work_order",'"test"',False),] ),
    ("wo:test", [SF(models.Order,"work_order","test",False),] ),
    ("-wo:test", [SF(models.Order,"work_order","test",True),] ),
    ('wo:"test"', [SF(models.Order,"work_order",'"test"',False),] ),
    ("description:test", [SF(models.Order,"description","test",False),] ),
    ("-description:test", [SF(models.Order,"description","test",True),] ),
    ('description:"test"', [SF(models.Order,"description",'"test"',False),] ),
    ################# Order->Date Search
    ("date:1/2/3", [SF(models.Order,"date","1/2/3",False),] ),
    ("-date:1/2/3", [SF(models.Order,"date","1/2/3",True),] ),
    ("date:>1/2/3", [SF(models.Order,"date",">1/2/3",False),] ),
    ("entered:1/2/3", [SF(models.Order,"date","1/2/3",False),] ),
    ("-entered:1/2/3", [SF(models.Order,"date","1/2/3",True),] ),
    ("entered:>=1/2/3", [SF(models.Order,"date",">=1/2/3",False),] ),
    ("origin_date:1/2/3", [SF(models.Order,"origin_date","1/2/3",False),] ),
    ("-origin_date:1/2/3", [SF(models.Order,"origin_date","1/2/3",True),] ),
    ("origin_date:<1/2/3", [SF(models.Order,"origin_date","<1/2/3",False),] ),
    ("origin:1/2/3", [SF(models.Order,"origin_date","1/2/3",False),] ),
    ("-origin:1/2/3", [SF(models.Order,"origin_date","1/2/3",True),] ),
    ("origin:<=1/2/3", [SF(models.Order,"origin_date","<=1/2/3",False),] ),
    ("due_date:1/2/3", [SF(models.Order,"due_date","1/2/3",False),] ),
    ("-due_date:1/2/3", [SF(models.Order,"due_date","1/2/3",True),] ),
    ("due_date:=<1/2/3", [SF(models.Order,"due_date","=<1/2/3",False),] ),
    ("due:1/2/3", [SF(models.Order,"due_date","1/2/3",False),] ),
    ("-due:1/2/3", [SF(models.Order,"due_date","1/2/3",True),] ),
    ("due:=>1/2/3", [SF(models.Order,"due_date","=>1/2/3",False),] ),
    ################# Various Objects

    ]

class TokenizerCase(test.TestCase):
    def test_basic(self):
        """ """
        for _input, result in TESTS:
            with self.subTest(_input = _input, result = result):
                output = search._tokenize(_input)
                self.assertEqual(output,result)
