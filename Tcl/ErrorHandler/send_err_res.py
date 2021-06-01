Error_list = {
    "NP": " Not Provided",
    "EL": " extends the provided limits",
    "SL": " is too short.",
    "IN": " is not numeric.",
    "NV": " is not valid."
}


def raiseError(fieldnm, ET):
    return fieldnm + Error_list[ET]


DB_Error_list = {
    "FK": "Foreign_key Error",
    "FNF": "File Not Found",
    "CE": "Credentials Error",
    "SW": "Something Goes Wrong!",
    "NR": "No Record Found",
    "NE": "Network Error",
    "API_CONFIG_NOT_FOUND": "Api configuration not found!",
    "PAS": "Products are already synched."
}


def raiseDBError(ET):
    return DB_Error_list[ET]
