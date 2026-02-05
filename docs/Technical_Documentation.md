## Performance-Optimizations

### InfluxDBService: Caching behavior of `getTotalPointCountForAllMeasurements`

The method `getTotalPointCountForAllMeasurements` returns the total number of data points across all measurements in the InfluxDB database. Since this query is very expensive, the result is cached together with the current date inside the service.

- On each call, the method checks if a value for today's date is already present in the cache.
- If so, the cached value is returned immediately and no new database query is executed.
- If the cached date is older than today or no value is stored yet, the query is executed, the cache is updated, and the new value is returned.

This ensures that the expensive counting operation is performed at most once per day, and all further calls on the same day are very fast.

## StatisticsService

The `StatisticsService` class provides various statistical operations and aggregations for the available InfluxDB measurements. It acts as a central point for collecting, aggregating, and serving statistics to the application or dashboard.

### Main Responsibilities

- **Continuous Queries Management:**  
  The service can create continuous queries in InfluxDB to automatically aggregate data (e.g., daily averages) for each measurement. This is handled by the `handleContinuousQueries()` method, which checks for existing queries and creates new ones if needed.

- **Latest Measurements:**  
  The `getLatestMeasurements()` method retrieves the most recent data point for each available measurement.

- **Point Counts:**  
  The `getPointCount()` method returns the number of data points for each measurement.

- **Minimum and Maximum Values:**  
  The `getMinValues()` and `getMaxValues()` methods return the minimum and maximum values (with timestamps) for each measurement.

- **Averages:**  
  The `getAverages()` method calculates the mean value for each measurement.

- **Statistics Aggregation:**  
  The `getStatistics()` method aggregates all the above information into a single `Statistics` object for easy consumption.

### Notes

- The set of available measurements is defined in the service and can be adjusted as needed.
- The service relies on `InfluxDBService` for all database interactions and data retrieval.
- Error handling is implemented to ensure that failures in individual queries do not break the overall statistics aggregation.

This service is intended to support dashboard and reporting features by providing fast access to key metrics and statistics from the InfluxDB time series database.

## Statistics

The `Statistics` class is a data container that aggregates and exposes key statistical information about the available measurement data from InfluxDB. It is used as a return type by the `StatisticsService` to provide a comprehensive snapshot of the current state of all relevant measurements.

### Fields

- **overallTotalPointCount**:  
  The total number of data points across all measurements (expensive to compute, see caching in `InfluxDBService`).

- **averageValues**:  
  A map from measurement name to the average (mean) value for that measurement.

- **latestMeasurements**:  
  A map from measurement name to the latest `Measurement` object (including sensor metadata and the most recent data point).

- **measurementPointCount**:  
  A map from measurement name to the number of data points for that measurement.

- **minValues / maxValues**:  
  Maps from measurement name to the minimum/maximum value (and timestamp) for each measurement.

### Purpose

This class is designed to be used as a DTO (Data Transfer Object) for dashboard features in the Angular Frontend, enabling efficient transfer and access to all relevant statistics in a single object.