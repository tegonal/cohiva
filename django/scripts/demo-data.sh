#!/bin/bash

save_demo_data() {
    mysqldump --events --create-options --quote-names --skip-extended-insert -p,MD822%0893jf -ucohiva-demo cohiva-demo_django_test > ./demo-data/demo-data.sql
    #mysqldump --events --create-options --quote-names --skip-extended-insert -p,MD822%0893jf -ucohiva-demo cohiva-demo_django > ./demo-data/demo-data_from_prod.sql
}

load_demo_data() {
    mysql -p,MD822%0893jf -ucohiva-demo cohiva-demo_django_test < ./demo-data/demo-data.sql
}

deploy_demo_data_to_prod() {
    mysql -p,MD822%0893jf -ucohiva-demo cohiva-demo_django < ./demo-data/demo-data.sql
    rsync -av --delete demo-data/smedia/* ../django-production/smedia/
}

save_demo_data
#load_demo_data
#deploy_demo_data_to_prod
