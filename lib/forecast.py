import datetime

VFR = 'VFR'
MVFR = 'MVFR'
IFR = 'IFR'
LIFR = 'LIFR'

BROKEN = 'BKN'
OVERCAST = 'OVC'

THRESH_MVFR_CEILING = 3000
THRESH_IFR_CEILING = 1000
THRESH_LIFR_CEILING = 500
THRESH_MVFR_VISIBILITY = 5
THRESH_IFR_VISIBILITY = 3
THRESH_LIFR_VISIBILITY = 1

def findMinimumCeiling(forecast):
    ceiling = None
    if forecast.iter('sky_condition') is None:
        return None
    for skyCondition in forecast.iter('sky_condition'):
        layer = skyCondition.attrib
        coverage = layer['sky_cover']
        if coverage not in [BROKEN, OVERCAST]:
            continue
        base = int(layer['cloud_base_ft_agl'])
        if (ceiling is None) or (base < ceiling):
            ceiling = base
    return ceiling

def findIndexForCondition(items, condition):
    for item in items:
        if condition(item):
            return item
    return None

def minimumDate(first, second):
    if first > second:
        return second
    if second > first:
        return first
    return first

def maximumDate(first, second):
    if first > second:
        return first
    if second > first:
        return second
    return first

def overrideForecastPeriod(period, overrides):
    periodStartTime = datetime.datetime.strptime(period.find('fcst_time_from').text, '%Y-%m-%dT%H:%M:%SZ')
    periodEndTime = datetime.datetime.strptime(period.find('fcst_time_to').text, '%Y-%m-%dT%H:%M:%SZ')
    periodVisibility = period.find('visibility_statute_mi').text
    periodCeiling = findMinimumCeiling(period)
    periodWindSpeed = 0
    periodWindGust = 0
    periodLightning = False
    if period.find('wind_speed_kt') is not None:
        periodWindSpeed = int(period.find('wind_speed_kt').text)
    if period.find('wind_gust_kt') is not None:
        periodWindGust = int(period.find('wind_gust_kt').text)
    if period.find('raw_text') is not None:
        rawText = period.find('raw_text').text
        periodLightning = False if rawText.find('LTG') == -1 else True

    periodForecast = { 'visibility': periodVisibility, 'ceiling': periodCeiling, 'windSpeed': periodWindSpeed, 'windGust': periodWindGust, 'lightning': periodLightning }
    def overlaps(overridePeriod):
        overrideStartTime = datetime.datetime.strptime(overridePeriod.find('fcst_time_from').text, '%Y-%m-%dT%H:%M:%SZ')
        overrideEndTime = datetime.datetime.strptime(overridePeriod.find('fcst_time_to').text, '%Y-%m-%dT%H:%M:%SZ')
        return (overrideStartTime < periodEndTime and overrideStartTime >= periodStartTime) or (overrideEndTime > periodStartTime and overrideEndTime <= periodEndTime)
    override = findIndexForCondition(overrides, overlaps)
    if (override is not None):
        overrideStartTime = datetime.datetime.strptime(override.find('fcst_time_from').text, '%Y-%m-%dT%H:%M:%SZ')
        overrideEndTime = datetime.datetime.strptime(override.find('fcst_time_to').text, '%Y-%m-%dT%H:%M:%SZ')
        overrideVisibility = override.find('visibility_statute_mi') is not None and override.find('visibility_statute_mi').text
        overrideCeiling = findMinimumCeiling(override)
        overrideWindSpeed = override.find('wind_speed_kt') is not None and int(override.find('wind_speed_kt').text)
        overrideWindGust = override.find('wind_gust_kt') is not None and int(override.find('wind_gust_kt').text)
        overrideLightning = False
        if override.find('raw_text') is not None:
            lightning = False if override.find('raw_text').text.find('LTG') == -1 else True

        overrideForecast = {
            'visibility': overrideVisibility or periodVisibility,
            'ceiling': overrideCeiling or periodCeiling,
            'windSpeed': overrideWindSpeed or periodWindSpeed,
            'windGust': overrideWindGust or periodWindGust,
            'lightning': overrideLightning or periodLightning
        }
        newPeriods = [
            { "startTime": periodStartTime, "endTime": maximumDate(periodStartTime, overrideStartTime), "forecast": periodForecast },
            { "startTime": maximumDate(periodStartTime, overrideStartTime), "endTime": minimumDate(overrideEndTime, periodEndTime), "forecast": overrideForecast },
            { "startTime": minimumDate(overrideEndTime, periodEndTime), "endTime": periodEndTime, "forecast": periodForecast }
        ]
        return [i for i in newPeriods if i["startTime"] != i["endTime"]]

    return [{ "startTime": periodStartTime, "endTime": periodEndTime, "forecast": periodForecast }]

def findFlightCategory(forecast):
    category = VFR
    ceiling = int(forecast["ceiling"] or THRESH_MVFR_CEILING)
    visibility = float(forecast["visibility"])
    if ceiling is None:
        return
    if visibility is None:
        return

    ceilingCategory = VFR
    if ceiling < THRESH_LIFR_CEILING:
        ceilingCategory = LIFR
    elif ceiling < THRESH_IFR_CEILING:
        ceilingCategory = IFR
    elif ceiling < THRESH_MVFR_CEILING:
        ceilingCategory = MVFR

    visibilityCategory = VFR
    if visibility < THRESH_LIFR_VISIBILITY:
        visibilityCategory = LIFR
    elif visibility < THRESH_IFR_VISIBILITY:
        visibilityCategory = IFR
    elif visibility < THRESH_MVFR_VISIBILITY:
        visibilityCategory = MVFR

    categoryPriority = [LIFR, IFR, MVFR, VFR]
    if categoryPriority.index(ceilingCategory) < categoryPriority.index(visibilityCategory):
        category = ceilingCategory
    else:
        category = visibilityCategory

    return category

def generateForecast(taf, stationId):
    def isTemp(forecast):
        return forecast.find('change_indicator') is not None and ((forecast.find('change_indicator').text == "TEMPO") or forecast.find('change_indicator').text == "PROB")
    forecastPeriodsInitial = [i for i in taf.iter('forecast') if isTemp(i) == False]
    forecastPeriodOverrides = [i for i in taf.iter('forecast') if isTemp(i) == True]

    forecastPeriods = [chunk for period in forecastPeriodsInitial for chunk in overrideForecastPeriod(period, forecastPeriodOverrides)]
    for forecastPeriod in forecastPeriods:
        forecastPeriod["flightCategory"] = findFlightCategory(forecastPeriod["forecast"])

    return forecastPeriods
