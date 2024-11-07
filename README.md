
# Conversation for Published records
---

To make the conversation available for published records:

    Copy records.py to <instance-folder>/site/<instance-name> folder
    Add the following entry in <instance-folder>/site/setup.cfg
    invenio_base.apps =
        <instance-name>_records = <instance-name>.records:register_filters
    cd <instance-folder>
    invenio-cli shell
    cd site
    pip install -e .
    Copy html files to respective folders in your <instance-folder>/templates
    Restart your server

