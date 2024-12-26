MEASUREMENT SITES
lat ->"filterAttributes_location_lat"
lon ->"filterAttributes_location_lon"
agency -> "filterAttributes_agency"
publicationtime -> "datexPublicationData_publicationTime"
sitetable_id -> "datexPublicationData_measurementSiteTable_[]__id"
sitetable_version -> "datexPublicationData_measurementSiteTable_[]__version"
id -> "datexPublicationData_measurementSiteTable_[]_measurementSite_[]__id"
version ->"datexPublicationData_measurementSiteTable_[]_measurementSite_[]__version"
measurementsepecificcharacteristicindex -> "datexPublicationData_measurementSiteTable_[]_measurementSite_[]_measurementSpecificCharacteristics_[]_index": 1,
 
MEASUREMENT CHARACTERISTICS
index -> "datexPublicationData_measurementSiteTable_[]_measurementSite_[]_measurementSpecificCharacteristics_[]_index": 1,
period -> "datexPublicationData_measurementSiteTable_[]_measurementSite_[]_measurementSpecificCharacteristics_[]_measurementSpecificCharacteristics_period"
specificmeasurementvaluetype -> "datexPublicationData_measurementSiteTable_[]_measurementSite_[]_measurementSpecificCharacteristics_[]_measurementSpecificCharacteristics_specificMeasurementValueType_value"
specificlanes -> "datexPublicationData_measurementSiteTable_[]_measurementSite_[]_measurementSpecificCharacteristics_[]_measurementSpecificCharacteristics_specificLane_[]_laneNumber"