import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

categories_sql = """
INSERT INTO public.categories_elettrodomestico (name, description) VALUES
('Kitchen', 'Appliances used in kitchen for cooking and food preparation'),
('Laundry', 'Appliances for washing and drying clothes'),
('Climate', 'Heating and cooling devices'),
('Entertainment', 'TVs and entertainment systems'),
('Personal Care', 'Hair dryers, irons, and grooming devices'),
('Storage', 'Refrigeration and preservation')
ON CONFLICT (name) DO NOTHING;
"""

devices_sql = """
INSERT INTO public.devices (name, average_watts, standby_watts, category_id)
SELECT v.name, v.average_watts, v.standby_watts, c.id
FROM (VALUES
    ('Microwave', 1000, 3, 'Kitchen'),
    ('Dishwasher', 1800, 2, 'Kitchen'),
    ('Oven', 2500, 2, 'Kitchen'),
    ('Toaster', 800, 0, 'Kitchen'),
    ('Coffee Maker', 1200, 1, 'Kitchen'),
    ('Electric Kettle', 1500, 1, 'Kitchen'),
    ('Washing Machine', 400, 2, 'Laundry'),
    ('Clothes Dryer', 3500, 1, 'Laundry'),
    ('Clothes Iron', 1400, 0, 'Laundry'),
    ('Heater (Portable)', 1200, 1, 'Climate'),
    ('AC Unit (Room)', 1300, 5, 'Climate'),
    ('Ceiling Fan', 75, 1, 'Climate'),
    ('Flat Screen TV (42")', 120, 15, 'Entertainment'),
    ('Gaming Console', 150, 20, 'Entertainment'),
    ('Home Theater System', 200, 30, 'Entertainment'),
    ('Hair Dryer', 1500, 0, 'Personal Care'),
    ('Electric Blanket', 80, 0, 'Personal Care'),
    ('Dehumidifier', 700, 2, 'Personal Care'),
    ('Refrigerator', 700, 10, 'Storage'),
    ('Freezer', 600, 8, 'Storage')
) AS v(name, average_watts, standby_watts, category_name)
JOIN public.categories_elettrodomestico c ON c.name = v.category_name
ON CONFLICT DO NOTHING;
"""

try:
    cursor.execute(categories_sql)
    cursor.execute(devices_sql)
    conn.commit()

except Exception as e:
    conn.rollback()
finally:
    cursor.close()
    conn.close()
