TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER Zone_Insert_Trigger AFTER INSERT ON Zones\nFOR EACH ROW\n  BEGIN\n    UPDATE Monitors SET ZoneCount=(SELECT COUNT(*) FROM Zones WHERE MonitorId=NEW.MonitorId) WHERE Monitors.Id=NEW.MonitorID;\n  END' 'CREATE DEFINER=`root`@`localhost` TRIGGER Zone_Delete_Trigger AFTER DELETE ON Zones\nFOR EACH ROW\n  BEGIN\n    UPDATE Monitors SET ZoneCount=(SELECT COUNT(*) FROM Zones WHERE MonitorId=OLD.MonitorId) WHERE Monitors.Id=OLD.MonitorID;\n  END'
sql_modes=1436549152 1436549152
definers='root@localhost' 'root@localhost'
client_cs_names='latin1' 'latin1'
connection_cl_names='latin1_swedish_ci' 'latin1_swedish_ci'
db_cl_names='latin1_swedish_ci' 'latin1_swedish_ci'
created=167519050547 167519050549
