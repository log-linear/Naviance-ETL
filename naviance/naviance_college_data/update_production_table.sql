/*
Author: Victor Faner

Description: Query to update the CollegeData.Naviance.naviance_college_data with 
             non-matched rows from corresponding CollegeData_STAGING table. To 
             be run AFTER running .py scripts to upload Staging tables.
*/

BEGIN TRAN update_college_data

    BEGIN TRY

        INSERT INTO CollegeData.Naviance.naviance_college_data

        SELECT *

        FROM CollegeData_STAGING.Naviance.naviance_college_data AS s

        WHERE NOT EXISTS (

            SELECT *       
                            
            FROM CollegeData.Naviance.naviance_college_data AS p   
                                            
            WHERE 
                ISNULL(p.naviance_college_id, '')       = ISNULL(s.naviance_college_id, '')
                AND ISNULL(p.naviance_college_name, '') = ISNULL(s.naviance_college_name, '')
                AND ISNULL(p.ceeb_code, '')             = ISNULL(s.ceeb_code, '')

            )
                       
        COMMIT
                
    END TRY

    BEGIN CATCH
                
        ROLLBACK TRAN update_college_data

    END CATCH