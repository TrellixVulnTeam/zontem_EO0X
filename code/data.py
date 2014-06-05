#!/usr/bin/env python

"""
Classes to support monthly temperature series.

Typically these are series of data from a station
(associated Station instance), but may also be synthesized
series (for example, when a zone's station's time series are
combined).
"""

#: The value that is used to indicate a bad or missing data point.
MISSING = 9999.0

def invalid(v):
    return v == MISSING

def valid(v):
    return not invalid(v)


class Station(object):
    """A station's metadata.

    This holds the information about a single station.

    The attributes stored depend entirely on the IO code that
    creates the instance. For GHCN-M V3 see the ghcn.py file.
    """

    def __init__(self, **values):
        self.__dict__.update(values)

    def __repr__(self):
        return "Station(%r)" % self.__dict__


class Series(object):
    """Monthly Series of data.

    (conventionally the data are average monthly temperature values
    in degrees Celsius)

    All the instance variables should be treated as read-only.

    An instance contains a series of monthly data accessible via the
    `series` property.

    A series has data from `first_year` (starting in January)
    through to `last_year` (ending in December). A series always
    consists of a whole number of years and includes both
    `first_year` and `last_year`.

    Conventionally, the `station` property refers to the Station
    instance for this series.

    Only the `add_year` method (which appends a single year of
    data) can be used to change the instance after it has been
    created.

    This class is not designed for subclassing. Please do not do it.

    When creating instances, the `first_year` parameter must be
    supplied:

    :Ivar first_year:
        Set the first year of the series.  Data that are
        subsequently added using add_year will be ignored if they
        precede first_year (a typical use is to set first_year to 1880
        for all records, ensuring that they all start at the same year).
    """

    def __init__(self, first_year, **k):
        self.first_year = first_year
        self.series = []

        self.__dict__.update(k)

    def __repr__(self):
        # Assume it is a station record with a uid.
        return "Series(uid=%r)" % getattr(self, 'uid',
          "<%s>" % id(self))

    def __len__(self):
        """The length of the series."""
        return len(self.series)

    @property
    def last_year(self):
        """The year of the last value in the series."""
        return self.first_year + len(self.series) // 12 - 1

    def good_count(self):
        """The number of good values in the data."""
        bad_count = self.series.count(MISSING)
        return len(self.series) - bad_count

    # Year's worth of missing data
    missing_year = [MISSING]*12

    def has_data_for_year(self, year):
        return self.first_year <= year <= self.last_year

    def get_a_year(self, year):
        """Get the time series data for a year."""
        if self.has_data_for_year(year):
            start = (year - self.first_year) * 12
            stop = start + 12
            return self.series[start:stop]
        else:
            return list(self.missing_year)

    # Mutators below here

    def add_year(self, year, data):
        """Add a year's worth of data.  *data* should be a sequence of
        length 12.  Years must be added in increasing order (though the
        sequence is permitted to have gaps in, and these will be filled
        with MISSING).
        """

        assert len(data) == 12

        if not self.first_year:
            self.first_year = year
        else:
            # We have data already, so we may need to pad with missing months
            # Note: This assumes the series is a whole number of years.
            gap = year - self.last_year - 1
            if gap > 0:
                self.series.extend([MISSING] * (gap * 12))
        assert len(self) % 12 == 0
        if year < self.first_year:
            # Ignore years before the first year.
            return
        assert year == self.last_year + 1
         
        self.series.extend(data)
