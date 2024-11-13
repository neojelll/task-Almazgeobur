workspace {

    model {

        User = person "User" "user" 

        SoftwareSystem = softwareSystem "Task-almazgeobur" "Geting a file\nReport generation" {

            Api = container "API Gateway" "Handles and routes HTTP requests" "FastAPI"

            Celery = container "Celery" "Create and manage tasks" "Celery" {
                tags "CeleryForm"
            }

            Cache = container "Cache" "Stored key-value: hash-report" "Redis"

            DataBase = container "DataBase" "Stores tasks and products and reports" "PostrgeSQL" {
                tags "DatabaseForm"
            }
            
            LLM = container "LLM" "Generate reports\nused GigaChat API due to the closure of OpenAI and Claude API in the Russian Federation" "GigaChat API" {
                tags "ExternalSystem"
            }

            User -> Api "Uses"
            Api -> Celery "send_data"
            Celery -> DataBase "create_records"
            Celery -> Cache "create_records"
            Celery -> LLM "response_report"
            Api -> Cache "get_report"
            Api -> DataBase "get_report"

        }
    }

    views {

        systemContext SoftwareSystem {
            include *
            autolayout tb
        } 
        
        container SoftwareSystem {
            include *
            autolayout tb
        }
        

        styles {

            element "Element" {
                color white
            }

            element "Person" {
                background #000033
                shape Person
                stroke white
                metadata False
                strokeWidth 4
            }

            element "Software System" {
                shape RoundedBox
                background #3399FF
                stroke white
                metadata False
                strokeWidth 4
            }

            element "Container" {
                shape RoundedBox
                background #003366
                stroke white
                strokeWidth 4
            }
            
            element "ExternalSystem" {
                shape Box
                background #606060
                shape WebBrowser
            }

            element "DatabaseForm" {
                shape cylinder
            }
            
            element "CeleryForm" {
                shape pipe
            }

        }
        
    }

}
