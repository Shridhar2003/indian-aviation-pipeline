-- ============================================
-- 1. ROUTE SUMMARY
-- ============================================
CREATE OR REPLACE TABLE indian_flights.route_summary AS
SELECT
    estDepartureAirport     AS origin,
    estArrivalAirport       AS destination,
    COUNT(*)                AS total_flights,
    ROUND(AVG(flight_duration_mins), 1) AS avg_duration_mins,
    ROUND(MIN(flight_duration_mins), 1) AS min_duration_mins,
    ROUND(MAX(flight_duration_mins), 1) AS max_duration_mins,
    COUNT(DISTINCT icao24)  AS unique_aircraft
FROM indian_flights.raw_flights
WHERE
    flight_duration_mins BETWEEN 30 AND 600
    AND estDepartureAirport IS NOT NULL
    AND estArrivalAirport IS NOT NULL
GROUP BY 1, 2
ORDER BY total_flights DESC;
-- ============================================
-- 2. AIRPORT DAILY TRAFFIC
-- ============================================
CREATE OR REPLACE TABLE indian_flights.airport_daily_traffic AS
SELECT
    airport_name,
    airport_icao,
    CAST(flight_date AS DATE) AS flight_date,
    COUNTIF(flight_type = 'arrival')   AS arrivals,
    COUNTIF(flight_type = 'departure') AS departures,
    COUNT(*)                            AS total_movements
FROM indian_flights.raw_flights
GROUP BY 1, 2, 3
ORDER BY flight_date DESC, total_movements DESC;
-- ============================================
-- 3. FLIGHT FEATURES
-- ============================================
CREATE OR REPLACE TABLE indian_flights.flight_features AS
SELECT
    icao24,
    callsign,
    estDepartureAirport         AS origin,
    estArrivalAirport           AS destination,
    airport_name,
    flight_type,
    flight_duration_mins,
    CAST(flight_date AS DATE)   AS flight_date,
    EXTRACT(DAYOFWEEK FROM CAST(flight_date AS DATE)) AS day_of_week,
    EXTRACT(HOUR FROM firstSeen_dt) AS departure_hour,
    CASE
        WHEN flight_duration_mins < 60  THEN 'Short Haul'
        WHEN flight_duration_mins < 150 THEN 'Medium Haul'
        WHEN flight_duration_mins < 300 THEN 'Long Haul'
        ELSE 'Ultra Long'
    END AS duration_category,
    CASE
        WHEN estDepartureAirport IN ('VIDP','VABB','VOBL','VOMM','VECC','VOHB')
         AND estArrivalAirport   IN ('VIDP','VABB','VOBL','VOMM','VECC','VOHB')
        THEN 'Domestic'
        ELSE 'International'
    END AS route_type
FROM indian_flights.raw_flights
WHERE 
    flight_duration_mins BETWEEN 30 AND 600
    AND estDepartureAirport IS NOT NULL
    AND estArrivalAirport IS NOT NULL;
