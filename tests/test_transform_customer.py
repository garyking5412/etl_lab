import pytest
import pandas as pd

from etl.transform import clean_customers

def test_no_null_customer_id():
    """Test rằng clean_customers loại bỏ các dòng có customer_id null"""
    df = pd.DataFrame({
        "customer_id": [1, None, 3, None],
        "first_name": ["Alice", "Bob", "Charlie", "David"],
        "signup_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "email": ["email1@abc.com", "email1@abc.com", None, "email3@gmail.com"],
        "phone": ["20240101", "20240102", "20240103", None],
        "country": ["2024-01-01", None, None, "USA"],
        "is_active": [True, False, True, False]
    })
    
    df_clean = clean_customers(df)
    
    assert df_clean["customer_id"].notna().all(), "All customer_id should be non-null"
    assert len(df_clean) == 1, "Should have 1 ROW left after removing null"

def test_boolean_conversion():
    """Test rằng is_active được chuyển đổi sang boolean"""
    df = pd.DataFrame({
        "customer_id": [1, 2],
        "first_name": ["Alice", "Bob"],
        "signup_date": ["2024-01-01", "2024-01-02"],
        "email": ["email1@abc.com", "email1@abc.com"],
        "phone": ["20240101", "20240102"],
        "country": ["USA", "USA"],
        "is_active": ["True", "False"]
    })
    
    df_clean = clean_customers(df)
    
    assert df_clean["is_active"].dtype == bool, "is_active should be boolean type"

def test_phone_formatting():
    """Test rằng phone được chuyển đổi sang định dạng số điện thoại chuẩn"""
    df = pd.DataFrame({
        "customer_id": [1, 2],
        "first_name": ["Alice", "Bob"],
        "signup_date": ["2024-01-01", "2024-01-02"],
        "email": ["email1@abc.com", "email1@abc.com"],
        "phone": ["20240101", "20240102"],
        "country": ["USA", "USA"],
        "is_active": ["True", "False"]
    })
    
    df_clean = clean_customers(df)
    print('phone type: ' + str(df_clean["phone"].dtype))
    
    assert df_clean["phone"].dtype == 'string', "phone should be string type"

def test_signup_date_conversion():
    """Test rằng signup_date được chuyển đổi sang datetime"""
    df = pd.DataFrame({
        "customer_id": [1, 2],
        "first_name": ["Alice", "Bob"],
        "signup_date": ["2024-01-01", "2024-01-02"],
        "email": ["email1@abc.com", "email1@abc.com"],
        "phone": ["20240101", "20240102"],
        "country": ["USA", "USA"],
        "is_active": ["True", "False"]
    })
    
    df_clean = clean_customers(df)
    print('signup_date type: ' + str(df_clean["signup_date"].dtype))
    assert pd.api.types.is_datetime64_any_dtype(df_clean["signup_date"]), "signup_date should be datetime type"