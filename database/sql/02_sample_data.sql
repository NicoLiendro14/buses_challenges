USE school_buses;

INSERT INTO `buses` (
    title, year, make, model, body, chassis, engine, transmission,
    mileage, passengers, wheelchair, color, source, source_url,
    price, vin, location, us_region, description, scraped
) VALUES 
(
    '2018 Blue Bird Vision School Bus',
    '2018',
    'Blue Bird',
    'Vision',
    'Type C',
    'Ford',
    'Cummins ISB6.7',
    'Allison 2500RDS',
    '45000',
    '72',
    'Yes',
    'Yellow',
    'Blue Bird',
    'https://example.com/bus1',
    '85000',
    '1HGCM82633A123456',
    'New York',
    'NORTHEAST',
    'Excellent condition, wheelchair accessible, air conditioning',
    1
),
(
    '2019 Thomas C2 School Bus',
    '2019',
    'Thomas',
    'C2',
    'Type C',
    'Freightliner',
    'Cummins ISB6.7',
    'Allison 2500RDS',
    '35000',
    '77',
    'Yes',
    'Yellow',
    'Thomas',
    'https://example.com/bus2',
    '92000',
    '1HGCM82633A123457',
    'Los Angeles',
    'WEST',
    'Low mileage, wheelchair lift, rear air conditioning',
    1
),
(
    '2020 IC Bus CE Series',
    '2020',
    'IC Bus',
    'CE Series',
    'Type C',
    'Navistar',
    'MaxxForce 7',
    'Allison 2500RDS',
    '25000',
    '84',
    'Yes',
    'Yellow',
    'IC Bus',
    'https://example.com/bus3',
    '1HGCM82633A123458',
    'Chicago',
    'MIDWEST',
    'New condition, wheelchair accessible, both AC systems',
    1
);

INSERT INTO `buses_overview` (
    bus_id, mdesc, intdesc, extdesc, features, specs
) VALUES 
(
    1,
    '2018 Blue Bird Vision in excellent condition',
    'Clean interior with 72 passenger seats',
    'Yellow exterior with minimal wear',
    'Wheelchair lift, air conditioning, GPS tracking',
    'Engine: Cummins ISB6.7, Transmission: Allison 2500RDS'
),
(
    2,
    '2019 Thomas C2 with low mileage',
    '77 passenger seats, wheelchair lift',
    'Yellow exterior, excellent condition',
    'Wheelchair lift, rear AC, backup camera',
    'Engine: Cummins ISB6.7, Transmission: Allison 2500RDS'
),
(
    3,
    '2020 IC Bus CE Series, like new',
    '84 passenger seats, wheelchair accessible',
    'Yellow exterior, perfect condition',
    'Wheelchair lift, dual AC systems, GPS',
    'Engine: MaxxForce 7, Transmission: Allison 2500RDS'
);

INSERT INTO `buses_images` (
    name, url, description, image_index, bus_id
) VALUES 
(
    'blue_bird_front',
    'https://example.com/images/bus1_front.jpg',
    'Front view of Blue Bird Vision',
    0,
    1
),
(
    'blue_bird_side',
    'https://example.com/images/bus1_side.jpg',
    'Side view of Blue Bird Vision',
    1,
    1
),
(
    'thomas_front',
    'https://example.com/images/bus2_front.jpg',
    'Front view of Thomas C2',
    0,
    2
),
(
    'ic_bus_front',
    'https://example.com/images/bus3_front.jpg',
    'Front view of IC Bus CE',
    0,
    3
); 