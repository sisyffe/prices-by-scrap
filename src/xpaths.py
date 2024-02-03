from functools import lru_cache

# Table xpath
TABLE = "/html/body/div[1]/section/main/div/div/section/div/div/div/div[2]/div/div/div[2]" \
        "/div/div/div[3]/div[1]/div[2]/div[4]/div/div/div/div/div[2]/div/table"
TABLE_BIS = "/html/body/div/section/main/div/div/section/div/div/div/div[2]/div/div/div[2]" \
            "/div/div/div[3]/div[1]/div[2]/div[5]/div/div/div/div/div[2]/div/table"


# Title xpath
@lru_cache
def title(table: str = TABLE):
    return table + "/thead/tr[1]/th[1]/span/div/span[1]"


# Head of columns: name of the prices
# "{}" is the number of column
@lru_cache
def head_columns(table: str = TABLE):
    return table + "/thead/tr[2]/th[{}]/span/div/span[1]"


# Value of the table where the "{line}" is the line number and the "{column}" is the column number
@lru_cache
def value(table: str = TABLE):
    return table + "/tbody/tr[{line}]/td[{column}]"


# All countries where "{}" is the line number
@lru_cache
def countries(table: str = TABLE):
    return value(table).replace("{column}", "1").replace("{line}", "{}")
