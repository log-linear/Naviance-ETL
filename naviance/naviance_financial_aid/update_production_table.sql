/*
Author: Victor Faner

Description: Query to update the CollegeData.Naviance.scholar_financial_aid_awards with 
             non-matched rows from corresponding CollegeData_STAGING table. To 
             be run AFTER running .py scripts to upload Staging tables.
*/

BEGIN TRAN update_scholar_financial_awards

    BEGIN TRY

        MERGE CollegeData.Naviance.scholar_financial_aid_awards AS p

        USING CollegeData_STAGING.Naviance.scholar_financial_aid_awards AS s
            ON p.local_student_id = s.local_student_id
            AND p.naviance_scholarship_name = s.naviance_scholarship_name

        WHEN MATCHED
            AND ISNULL(p.scholarship_amount, 0)   != ISNULL(s.scholarship_amount, 0)
            AND ISNULL(p.naviance_college_id, 0)  != ISNULL(s.naviance_college_id, 0)
            AND ISNULL(p.naviance_categories, '') != ISNULL(s.naviance_categories, '')
            AND ISNULL(p.award_name, '')          != ISNULL(s.award_name, '')
            AND ISNULL(p.primary_aid_type, '')    != ISNULL(s.primary_aid_type, '')
            AND ISNULL(p.sub_type, '')            != ISNULL(s.sub_type, '')
            AND ISNULL(p.source, '')              != ISNULL(s.source, '')

            THEN UPDATE SET
                p.scholarship_amount   = s.scholarship_amount
                ,p.naviance_college_id = s.naviance_college_id
                ,p.naviance_categories = s.naviance_categories
                ,p.award_name          = s.award_name
                ,p.primary_aid_type    = s.primary_aid_type
                ,p.sub_type            = s.sub_type
                ,p.source              = s.source

        WHEN NOT MATCHED

            THEN INSERT (

                local_student_id
                ,naviance_scholarship_name
                ,scholarship_amount
                ,naviance_college_id
                ,naviance_categories
                ,award_name
                ,primary_aid_type
                ,sub_type
                ,source

            ) VALUES (

                s.local_student_id
                ,s.naviance_scholarship_name
                ,s.scholarship_amount
                ,s.naviance_college_id
                ,s.naviance_categories
                ,s.award_name
                ,s.primary_aid_type
                ,s.sub_type
                ,s.source

            );


        COMMIT
                
    END TRY

    BEGIN CATCH
                
        ROLLBACK TRAN update_scholar_financial_awards

    END CATCH
