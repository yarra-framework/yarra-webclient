CREATE SCHEMA quake_data;

CREATE MATERIALIZED VIEW quake_data.asset AS SELECT
	"AssetId" as asset_id,
	"Name" as name,
	"AssetTypeId" as asset_type_id,
	"ParentAssetId" as parent_asset_id,
	"ActiveFlag" as active_flag,
	"StatusId" as status_id,
	"CompanyId" as company_id,
	"CurrentLocationId" as current_location_id,
	"LastKnownLocationId" as last_known_location_id,
	"LastMovementDate" as last_movement_date,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."Asset" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.floor AS SELECT
	"FloorId" as floor_id,
	"Name" as name,
	"DisplayName" as display_name,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"BuildingId" as building_id
from quake."Floor" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.global_filter AS SELECT
	"GlobalFilterId" as global_filter_id,
	"Value" as value,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"FilterTypeId" as filter_type_id,
	"CompanyId" as company_id
from quake."GlobalFilter" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.location_filter AS SELECT
	"LocationFilterId" as location_filter_id,
	"Value" as value,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"FilterTypeId" as filter_type_id,
	"LocationId" as location_id
from quake."LocationFilter" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.location_group AS SELECT
	"LocationGroupId" as location_group_id,
	"Code" as code,
	"Name" as name,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"CompanyId" as company_id
from quake."LocationGroup" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.pam_delivery_records AS SELECT
	"Id" as id,
	"MsgId" as msg_id,
	"Message" as message,
	"SubscriberId" as subscriber_id,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."PamDeliveryRecords" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.pam_failed_delivery_records AS SELECT
	"Id" as id,
	"MsgId" as msg_id,
	"Message" as message,
	"SubscriberId" as subscriber_id,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."PamFailedDeliveryRecords" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.report AS SELECT
	"ReportModelId" as report_model_id,
	"CompanyId" as company_id,
	"Name" as name,
	"ReportType" as report_type,
	"Recurrence" as recurrence,
	"ReportFormat" as report_format,
	"EmailList" as email_list,
	"TzName" as tz_name,
	"RunTime" as run_time,
	"SsrsScheduleDefinition" as ssrs_schedule_definition,
	"SsrsSubscriptionId" as ssrs_subscription_id,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"ReportTypeInt" as report_type_int,
	"RecurrenceInt" as recurrence_int,
	"ReportFormatInt" as report_format_int,
	"BrowserDateTime" as browser_date_time,
	"IsScheduled" as is_scheduled,
	"Discriminator" as discriminator
from quake."Report" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.report_type_model AS SELECT
	"ReportTypeModelId" as report_type_model_id,
	"Name" as name,
	"Daily" as daily,
	"Weekly" as weekly,
	"Monthly" as monthly,
	"ReportType" as report_type,
	"AssetTypeId" as asset_type_id,
	"CompanyId" as company_id,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."ReportTypeModel" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.rule AS SELECT
	"RuleId" as rule_id,
	"RuleName" as rule_name,
	"RuleTypeId" as rule_type_id,
	"ActiveFlag" as active_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."Rule" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.rule_property AS SELECT
	"RulePropertyId" as rule_property_id,
	"RulePropertyTypeId" as rule_property_type_id,
	"Value" as value,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"RuleId" as rule_id
from quake."RuleProperty" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.subscriber AS SELECT
	"SubscriberId" as subscriber_id,
	"Value" as value,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"SubscriptionTypeId" as subscription_type_id,
	"CompanyId" as company_id,
	"Format" as format
from quake."Subscriber" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.subscriber_filter AS SELECT
	"SubscriberFilterId" as subscriber_filter_id,
	"Value" as value,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"FilterTypeId" as filter_type_id,
	"SubscriberId" as subscriber_id
from quake."SubscriberFilter" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.sysdiagrams AS SELECT
	"name" as name,
	"principal_id" as principal_id,
	"diagram_id" as diagram_id,
	"version" as version,
	"definition" as definition
from quake."sysdiagrams" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.system_configuration AS SELECT
	"SystemConfigurationId" as system_configuration_id,
	"AuditUserActions" as audit_user_actions,
	"AuditDbActions" as audit_db_actions,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"CompanyId" as company_id
from quake."SystemConfiguration" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.tag_label_template AS SELECT
	"TagLabelTemplateId" as tag_label_template_id,
	"Name" as name,
	"TemplateBody" as template_body,
	"ActiveFlag" as active_flag,
	"CompanyId" as company_id,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"AssetTypeId" as asset_type_id
from quake."TagLabelTemplate" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.tag_printer AS SELECT
	"TagPrinterId" as tag_printer_id,
	"Name" as name,
	"Manufacturer" as manufacturer,
	"Model" as model,
	"AssignedIdentifier" as assigned_identifier,
	"IpAddress" as ip_address,
	"PrinterPort" as printer_port,
	"BufferSize" as buffer_size,
	"SocketTimeout" as socket_timeout,
	"ActiveFlag" as active_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"LocationId" as location_id
from quake."TagPrinter" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.location AS SELECT
	"LocationId" as location_id,
	"Name" as name,
	"DisplayName" as display_name,
	"AccessionFlag" as accession_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"CompanyId" as company_id,
	"PositionX" as position_x,
	"PositionY" as position_y,
	"FloorId" as floor_id,
	"LocationGroupId" as location_group_id
from quake."Location" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.person AS SELECT
	"PersonId" as person_id,
	"Username" as username,
	"DomainName" as domain_name,
	"LastLogin" as last_login,
	"ActiveFlag" as active_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"CompanyId" as company_id
from quake."Person" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.tag AS SELECT
	"TagId" as tag_id,
	"Epc" as epc,
	"TagData" as tag_data,
	"ActiveFlag" as active_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"AssetId" as asset_id
from quake."Tag" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.tag_read AS SELECT
	"TagReadId" as tag_read_id,
	"TagId" as tag_id,
	"Epc" as epc,
	"Confidence" as confidence,
	"CapturedAt" AT TIME ZONE 'UTC' as captured_at,
	"ObservedAt" AT TIME ZONE 'UTC' as observed_at,
	"LocationId" as location_id,
	"ActiveFlag" as active_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."TagRead" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.patients_view AS SELECT
	"asset_id" as asset_id,
	"mrn" as mrn,
	"last_name" as last_name,
	"first_name" as first_name,
	"gender" as gender,
	"class" as class,
	"accession" as accession,
	"procedure" as procedure,
	"modality" as modality,
	"status" as status,
	"dob" as dob,
	"status_time" as status_time,
	"appt_time" as appt_time
from quake."patients_view" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.migration_history AS SELECT
	"MigrationId" as migration_id,
	"ContextKey" as context_key,
	"Model" as model,
	"ProductVersion" as product_version
from quake."__MigrationHistory" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.custom_help_page AS SELECT
	"Id" as id,
	"HtmlData" as html_data,
	"CompanyId" as company_id,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."CustomHelpPage" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.alert AS SELECT
	"AlertId" as alert_id,
	"AlertName" as alert_name,
	"AlertTypeId" as alert_type_id,
	"RuleId" as rule_id,
	"ActiveFlag" as active_flag,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."Alert" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.alert_log AS SELECT
	"AlertLogId" as alert_log_id,
	"AlertId" as alert_id,
	"LocationId" as location_id,
	"AssetId" as asset_id,
	"AlertMessage" as alert_message,
	"Resolved" as resolved,
	"ResolvedBy" as resolved_by,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"LastModified" AT TIME ZONE 'UTC' as last_modified
from quake."AlertLog" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.alert_properties AS SELECT
	"AlertPropertiesId" as alert_properties_id,
	"Address" as address,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"AlertId" as alert_id
from quake."AlertProperties" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.asset_data_config AS SELECT
	"AssetDataConfigId" as asset_data_config_id,
	"CompanyId" as company_id,
	"FieldName" as field_name,
	"DisplayLabel" as display_label,
	"isRequired" as is_required,
	"CustomField" as custom_field,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"DataFormat" as data_format,
	"isEnabled" as is_enabled,
	"AssetTypeId" as asset_type_id
from quake."AssetDataConfig" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.asset_type AS SELECT
	"AssetTypeId" as asset_type_id,
	"Name" as name,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."AssetType" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.building AS SELECT
	"BuildingId" as building_id,
	"Name" as name,
	"DisplayName" as display_name,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"CampusId" as campus_id
from quake."Building" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.campus AS SELECT
	"CampusId" as campus_id,
	"Name" as name,
	"DisplayName" as display_name,
	"Description" as description,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by,
	"CompanyId" as company_id
from quake."Campus" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.company AS SELECT
	"CompanyId" as company_id,
	"Name" as name,
	"Address1" as address1,
	"Address2" as address2,
	"City" as city,
	"State" as state,
	"Region" as region,
	"Country" as country,
	"PostalCode" as postal_code,
	"PhoneNumber" as phone_number,
	"DomainName" as domain_name,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."Company" WITH NO DATA;

CREATE MATERIALIZED VIEW quake_data.asset_data AS SELECT
	"AssetId" as asset_id,
	"Udfs1" as udfs1,
	"Udfs2" as udfs2,
	"Udfs3" as udfs3,
	"Udfs4" as udfs4,
	"Udfs5" as udfs5,
	"Udfs6" as udfs6,
	"Udfs7" as udfs7,
	"Udfs8" as udfs8,
	"Udfs9" as udfs9,
	"Udfs10" as udfs10,
	"Udfs11" as udfs11,
	"Udfs12" as udfs12,
	"Udfs13" as udfs13,
	"Udfs14" as udfs14,
	"Udfs15" as udfs15,
	"Udfs16" as udfs16,
	"Udfd1" as udfd1,
	"Udfd2" as udfd2,
	"Udfd3" as udfd3,
	"Udfd4" as udfd4,
	"CreatedOn" AT TIME ZONE 'UTC' as created_on,
	"CreatedBy" as created_by,
	"LastModified" AT TIME ZONE 'UTC' as last_modified,
	"LastModifiedBy" as last_modified_by
from quake."AssetData" WITH NO DATA;


CREATE MATERIALIZED VIEW quake_data.patient_data as 
SELECT "AssetData"."AssetId" AS asset_id,
	"AssetData"."Udfs1" AS mrn,
	"AssetData"."Udfs2" AS last_name,
	"AssetData"."Udfs3" AS first_name,
	"AssetData"."Udfs4" AS gender,
	"AssetData"."Udfs5" AS class,
	"AssetData"."Udfs6" AS accession,
	"AssetData"."Udfs7" AS procedure,
	"AssetData"."Udfs11" AS modality,
	"AssetData"."Udfs12" AS status,
	"AssetData"."Udfd1" AS dob,
	"AssetData"."Udfd2" AT TIME ZONE 'UTC' AS status_time,
	"AssetData"."Udfd3" AT TIME ZONE 'UTC' AS appt_time
FROM quake."AssetData" WITH NO DATA;




CREATE UNIQUE INDEX quake_data.asset_idx ON quake_data.asset (asset_id);
CREATE UNIQUE INDEX quake_data.floor_idx ON quake_data.floor (floor_id);
CREATE UNIQUE INDEX quake_data.global_filter_idx ON quake_data.global_filter (global_filter_id);
CREATE UNIQUE INDEX quake_data.location_filter_idx ON quake_data.location_filter (location_filter_id);
CREATE UNIQUE INDEX quake_data.location_group_idx ON quake_data.location_group (location_group_id);
CREATE UNIQUE INDEX quake_data.report_idx ON quake_data.report (report_model_id);
CREATE UNIQUE INDEX quake_data.report_type_model_idx ON quake_data.report_type_model (report_type_model_id);
CREATE UNIQUE INDEX quake_data.rule_idx ON quake_data.rule (rule_id);
CREATE UNIQUE INDEX quake_data.rule_property_idx ON quake_data.rule_property (rule_property_id);
CREATE UNIQUE INDEX quake_data.subscriber_idx ON quake_data.subscriber (subscriber_id);
CREATE UNIQUE INDEX quake_data.subscriber_filter_idx ON quake_data.subscriber_filter (subscriber_filter_id);
CREATE UNIQUE INDEX quake_data.sysdiagrams_idx ON quake_data.sysdiagrams (name);
CREATE UNIQUE INDEX quake_data.system_configuration_idx ON quake_data.system_configuration (system_configuration_id);
CREATE UNIQUE INDEX quake_data.tag_label_template_idx ON quake_data.tag_label_template (tag_label_template_id);
CREATE UNIQUE INDEX quake_data.tag_printer_idx ON quake_data.tag_printer (tag_printer_id);
CREATE UNIQUE INDEX quake_data.location_idx ON quake_data.location (location_id);
CREATE UNIQUE INDEX quake_data.person_idx ON quake_data.person (person_id);
CREATE UNIQUE INDEX quake_data.tag_idx ON quake_data.tag (tag_id);
CREATE UNIQUE INDEX quake_data.tag_read_idx ON quake_data.tag_read (tag_read_id);
CREATE UNIQUE INDEX quake_data.patients_view_idx ON quake_data.patients_view (asset_id);
CREATE UNIQUE INDEX quake_data.migration_history_idx ON quake_data.migration_history (migration_id);
CREATE UNIQUE INDEX quake_data.alert_idx ON quake_data.alert (alert_id);
CREATE UNIQUE INDEX quake_data.alert_log_idx ON quake_data.alert_log (alert_log_id);
CREATE UNIQUE INDEX quake_data.alert_properties_idx ON quake_data.alert_properties (alert_properties_id);
CREATE UNIQUE INDEX quake_data.asset_data_config_idx ON quake_data.asset_data_config (asset_data_config_id);
CREATE UNIQUE INDEX quake_data.asset_type_idx ON quake_data.asset_type (asset_type_id);
CREATE UNIQUE INDEX quake_data.building_idx ON quake_data.building (building_id);
CREATE UNIQUE INDEX quake_data.campus_idx ON quake_data.campus (campus_id);
CREATE UNIQUE INDEX quake_data.company_idx ON quake_data.company (company_id);
CREATE UNIQUE INDEX quake_data.asset_data_idx ON quake_data.asset_data (asset_id);
CREATE UNIQUE INDEX quake_data.patient_data_idx ON quake_data.patient_data (asset_id);

GRANT SELECT ON quake_data.asset TO yarra_dbconn;
GRANT SELECT ON quake_data.floor TO yarra_dbconn;
GRANT SELECT ON quake_data.global_filter TO yarra_dbconn;
GRANT SELECT ON quake_data.location_filter TO yarra_dbconn;
GRANT SELECT ON quake_data.location_group TO yarra_dbconn;
GRANT SELECT ON quake_data.pam_delivery_records TO yarra_dbconn;
GRANT SELECT ON quake_data.pam_failed_delivery_records TO yarra_dbconn;
GRANT SELECT ON quake_data.report TO yarra_dbconn;
GRANT SELECT ON quake_data.report_type_model TO yarra_dbconn;
GRANT SELECT ON quake_data.rule TO yarra_dbconn;
GRANT SELECT ON quake_data.rule_property TO yarra_dbconn;
GRANT SELECT ON quake_data.subscriber TO yarra_dbconn;
GRANT SELECT ON quake_data.subscriber_filter TO yarra_dbconn;
GRANT SELECT ON quake_data.sysdiagrams TO yarra_dbconn;
GRANT SELECT ON quake_data.system_configuration TO yarra_dbconn;
GRANT SELECT ON quake_data.tag_label_template TO yarra_dbconn;
GRANT SELECT ON quake_data.tag_printer TO yarra_dbconn;
GRANT SELECT ON quake_data.location TO yarra_dbconn;
GRANT SELECT ON quake_data.person TO yarra_dbconn;
GRANT SELECT ON quake_data.tag TO yarra_dbconn;
GRANT SELECT ON quake_data.tag_read TO yarra_dbconn;
GRANT SELECT ON quake_data.patients_view TO yarra_dbconn;
GRANT SELECT ON quake_data.migration_history TO yarra_dbconn;
GRANT SELECT ON quake_data.custom_help_page TO yarra_dbconn;
GRANT SELECT ON quake_data.alert TO yarra_dbconn;
GRANT SELECT ON quake_data.alert_log TO yarra_dbconn;
GRANT SELECT ON quake_data.alert_properties TO yarra_dbconn;
GRANT SELECT ON quake_data.asset_data_config TO yarra_dbconn;
GRANT SELECT ON quake_data.asset_type TO yarra_dbconn;
GRANT SELECT ON quake_data.building TO yarra_dbconn;
GRANT SELECT ON quake_data.campus TO yarra_dbconn;
GRANT SELECT ON quake_data.company TO yarra_dbconn;
GRANT SELECT ON quake_data.asset_data TO yarra_dbconn;
GRANT SELECT on quake_data.patient_data TO yarra_dbconn;
GRANT USAGE ON schema quake_data TO yarra_dbconn;	


REFRESH MATERIALIZED VIEW quake_data.asset WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.floor WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.global_filter WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.location_filter WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.location_group WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.pam_delivery_records WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.pam_failed_delivery_records WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.report WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.report_type_model WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.rule WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.rule_property WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.subscriber WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.subscriber_filter WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.sysdiagrams WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.system_configuration WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.tag_label_template WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.tag_printer WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.location WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.person WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.tag WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.tag_read WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.patients_view WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.migration_history WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.custom_help_page WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.alert WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.alert_log WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.alert_properties WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.asset_data_config WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.asset_type WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.building WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.campus WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.company WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.asset_data WITH DATA;
REFRESH MATERIALIZED VIEW quake_data.patient_data WITH DATA;

REFRESH MATERIALIZED VIEW quake_data.tag_read;
REFRESH MATERIALIZED VIEW quake_data.tag;
REFRESH MATERIALIZED VIEW quake_data.asset;
REFRESH MATERIALIZED VIEW quake_data.patient_data;
REFRESH MATERIALIZED VIEW quake_data.location;

CREATE OR REPLACE FUNCTION refresh_quake()
RETURNS void
SECURITY DEFINER
AS $$
BEGIN
refresh materialized view CONCURRENTLY quake_data.tag_read;
refresh materialized view CONCURRENTLY quake_data.tag;
refresh materialized view CONCURRENTLY quake_data.asset;
refresh materialized view CONCURRENTLY quake_data.patient_data;
refresh materialized view CONCURRENTLY quake_data.location;
RETURN;
END;
$$ LANGUAGE plpgsql;