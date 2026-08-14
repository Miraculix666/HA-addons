TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER Events_Day_update_trigger AFTER UPDATE ON Events_Day\nFOR EACH ROW\n  BEGIN\n    declare diff BIGINT default 0;\n\n    set diff = COALESCE(NEW.DiskSpace,0) - COALESCE(OLD.DiskSpace,0);\n    IF ( diff ) THEN\n      IF ( NEW.MonitorID != OLD.MonitorID ) THEN\n        UPDATE Event_Summaries SET DayEventDiskSpace=GREATEST(COALESCE(DayEventDiskSpace,0)-COALESCE(OLD.DiskSpace,0),0) WHERE Event_Summaries.MonitorId=OLD.MonitorId;\n        UPDATE Event_Summaries SET DayEventDiskSpace=COALESCE(DayEventDiskSpace,0)+COALESCE(NEW.DiskSpace,0) WHERE Event_Summaries.MonitorId=NEW.MonitorId;\n      ELSE\n        UPDATE Event_Summaries SET DayEventDiskSpace=GREATEST(COALESCE(DayEventDiskSpace,0)+diff,0) WHERE Event_Summaries.MonitorId=NEW.MonitorId;\n      END IF;\n    END IF;\n  END' 'CREATE DEFINER=`root`@`localhost` TRIGGER Events_Day_delete_trigger BEFORE DELETE ON Events_Day\nFOR EACH ROW BEGIN\n  UPDATE Event_Summaries SET\n  DayEvents = GREATEST(COALESCE(DayEvents,1)-1,0),\n  DayEventDiskSpace=GREATEST(COALESCE(DayEventDiskSpace,0)-COALESCE(OLD.DiskSpace,0),0)\n  WHERE Event_Summaries.MonitorId=OLD.MonitorId;\nEND'
sql_modes=1436549152 1436549152
definers='root@localhost' 'root@localhost'
client_cs_names='latin1' 'latin1'
connection_cl_names='latin1_swedish_ci' 'latin1_swedish_ci'
db_cl_names='latin1_swedish_ci' 'latin1_swedish_ci'
created=167519050511 167519050509
