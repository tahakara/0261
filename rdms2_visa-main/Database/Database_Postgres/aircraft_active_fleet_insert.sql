-- Aktif Uçak Filosu
-- Active Aircraft Fleet Data

INSERT INTO aircraft (code_number, brand, model, passenger_capacity, range_km, is_active, status) VALUES
-- TC-JDM
('TC-JDM', 'Boeing', '737-900ER', 180, 5800, true, 'active'),

-- Aktif Filo - Boeing Uçakları
('TC-JHX', 'Boeing', '737-800', 189, 5400, true, 'active'),
('TC-JJN', 'Boeing', '777-300ER', 349, 13650, true, 'active'),

-- Aktif Filo - Airbus Uçakları
('TC-JRA', 'Airbus', 'A321neo', 206, 7400, true, 'active'),
('TC-LSA', 'Airbus', 'A350-900', 325, 15000, true, 'active'),
('TC-LNA', 'Airbus', 'A330-300', 289, 11750, true, 'active');
