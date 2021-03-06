"""
SQLite Database Interface for Information

Copyright (c) 2014, 2015 Andrew Hawkins

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
Import Declarations
"""
import datetime as dt
import os
import re
import sqlite3
import sys

from forsteri.interface import data as idata

"""
Constant Declarations
"""
if os.name == "nt":
    DATA = "J:\\"
elif os.name == "posix":
    DATA = "/mnt/forecastdb/"
MASTER = ''.join([DATA, "master.db"])

"""
Product Information
"""
def getAttribute(attribute, connection=None):
    """
    Get all values for a single attribute.

    Args:
      attribute (str): The attribute to pull from the database.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      list of str: The attributes across all tuples.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve all items under attribute.
    cursor.execute("""SELECT {a} FROM information;""".format(a=attribute))

    # Fetch all rows.
    products = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return products

def getAllData(connection=None):
    """
    Get all data from the database.

    Args:
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      list of list of str: The data for all tuples and attributes.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve all data.
    cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information;""")

    # Fetch all rows.
    productData = cursor.fetchall()

    # Convert all None values to be empty strings.
    productData = ['' if attribute is None else attribute for product in\
        productData for attribute in product]
    productData = [productData[z : z + 6] for z in range(0,
        len(productData), 6)]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return productData

def getData(sieve, connection=None):
    """
    Get the data after filtering with a sieve.

    Args:
      sieve (dict of str: str): 
      connection (sqlite3.Connection, optional): 

    Returns:
      list of list of str: The data for tuples and attributes satifying the
        filter.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Define the sieve string.
    sieveStr = ''
    for (key, value) in sieve.items():
        if value != '' and value is not None:
            if key == "product" or key == "sku":
                sieveStr = ''.join([sieveStr, " AND ", key, " LIKE '", value,
                    "%'"])
            else:
                sieveStr = ''.join([sieveStr, " AND ", key, "='", value, "'"])


    # If the string is length zero, no sieve was input.
    if len(sieveStr) == 0:
        # Execute the statement to retrieve all data.
        cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information;""")
    else:
        # Cut the beginning of the string.
        sieveStr = sieveStr[5:]

        # Execute the statement to retrieve the sieve's information.
        cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information WHERE {s};""".format(s=sieveStr))

    # Fetch all rows.
    productData = cursor.fetchall()

    # Convert all None values to be empty strings.
    productData = ['' if attr is None else attr for product in productData for\
        attr in product]
    productData = [productData[z : z + 6] for z in range(0, len(productData),
        6)]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return productData

def getProduct(product, connection=None):
    """
    Get the data for a single product.

    Args:
      product (str): The name of the product.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      list of str: The data for a single tuple.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve the product's information.
    cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information WHERE product='{p}';""".format(p=product))

    # Fetch the first responded row.
    productData = cursor.fetchone()

    # Change None to be an empty string.
    productData = ['' if attr is None else attr for attr in productData]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return productData

def addProduct(productData, connection=None):
    """
    Add a product tuple to the database.

    Args:
      productData (dict of {str: str}): A tuple to add to the database. Must
        be of the form {"product": ?, "sku": ?, "account": ?, "class": ?,
        "category": ?, "subcategory": ?}.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Check if the product has been input or if it has already been added.
    if "product" not in productData.keys():
        return False

    # Initlialize the attribute and value lists.
    attrs = []
    values = []

    # Iterate over the inputted values and extract attributes.
    for (key, value) in productData.items():
        if value is None or value == '':
            continue
        else:
            attrs.append(key)
            values.append(value)

    # Convert to a valid string removing unnecessary characters.
    if len(attrs) == 1:
        attrs = re.sub("[',]", '', str(tuple(attrs)))
        values = re.sub(",", '', str(tuple(values)))
    else:
        attrs = re.sub("'", '', str(tuple(attrs)))
        values = str(tuple(values))

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to write the new data to the database.
    try:
        cursor.execute("""INSERT INTO information {a} VALUES {v}""".\
            format(a=attrs, v=values))
    except IntegrityError:
        print(productData["product"] + " already exists in the database.")

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def addProducts(newProducts, data, overwrite=False, connection=None):
    """
    Add many product tuples to the database.

    Args:
      newProducts (list of str): The list of new products.
      data (list of dict of str: str): The list of new data housed in
        dictionaries in the form {"product": ?, "sku": ?, "account": ?,
        "class": ?, "category": ?, "subcategory": ?}.
      overwrite (bool, optional): True if data already in the database
        should be overwritten with the new data, false otherwise.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Get the list of old products.
    oldProducts = getAttribute("product", connection)

    # Convert the new products to be a set.
    newProductsSet = set(newProducts)

    # Find the difference between the old and new data.
    addProducts = newProductsSet.difference(oldProducts)

    # Find the intersection of the old and new data.
    setProducts = newProductsSet.intersection(oldProducts)

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the rows in the input data.
    for productData in data:
        if productData["product"] in addProducts:
            # Initlialize the attribute and value lists.
            attrs = []
            values = []

            # Iterate over the inputted values and extract attributes.
            for (key, value) in productData.items():
                if value is None or value == '':
                    continue
                else:
                    attrs.append(key)
                    values.append(value)

            # Convert to a valid string removing unnecessary characters.
            if len(attrs) == 1:
                attrs = re.sub("[',]", '', str(tuple(attrs)))
                values = re.sub(",", '', str(tuple(values)))
            else:
                attrs = re.sub("'", '', str(tuple(attrs)))
                values = str(tuple(values))

            # Execute the command to write the new data to the database.
            cursor.execute("""INSERT INTO information {a} VALUES {v}""".\
                format(a=attrs, v=values))
        elif overwrite:
            # Set up the product for input
            productInput = "'" + productData["product"] + "'"

            # Iterate over the inputted values and update then in the database.
            for (key, value) in productData.items():
                change = key + "='" + value + "'"
                cursor.execute("""UPDATE information SET {c} WHERE product={p}
""".format(c=change, p=productInput))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getProductData(product, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to select all information for a product.
    cursor.execute("""SELECT * FROM information WHERE product='{p}'""".\
        format(p=product))

    # Fetch the data.
    data = cursor.fetchone()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return data

def getProductHash(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to pull all products that do not have a null sku.
    cursor.execute("""SELECT product, sku FROM information WHERE sku IS NOT 
NULL""")

    # Fetch all of the returned data.
    data = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    # Convert the data to a dictionary.
    match = {x[1]: x[0] for x in data}

    return match

def getProductNames(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to pull all products that do not have a null sku.
    cursor.execute("""SELECT DISTINCT product FROM information""")

    # Fetch all of the returned data.
    data = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    # Get only the names of the products.
    products = [x[0] for x in data]

    return products


def setProduct(product, productData, connection=None):
    """
    Set a product's tuple in the database.

    Args:
      product (str): The product currently in the database.
      productData (dict of {str: str}): A tuple to add to the database. Must
        be of the form {"product": ?, "sku": ?, "account": ?, "class": ?,
        "category": ?, "subcategory": ?}. Use None to set attributes to be
        NULL.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the input product data dictionary.
    for (key, value) in productData.items():
        if value == '':
            change = key + "=NULL"
        else:
            change = key + "='" + value + "'"
        cursor.execute("""UPDATE information SET {c} WHERE product='{p}'""".\
            format(c=change, p=product))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    # Change name if a new product is given.
    if "product" in productData:
        idata.changeName(product, productData["product"])

    return True

def setProducts(products, productData, connection=None):
    """
    Set a group of product's to have the same tuple (except unique) in the
    database.

    Args:
      product (str): The product currently in the database.
      productData (dict of {str: str}): A tuple to add to the database. Must
        be of the form {"product": ?, "sku": ?, "account": ?, "class": ?,
        "category": ?, "subcategory": ?}. Use None to set attributes to be
        NULL.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Check if product or sku is defined in the input data, if so return false.
    if productData["product"] != '' or productData["sku"] != '':
        return False

    # Define the input string for all products.
    change = ''
    for (key, value) in productData.items():
        if value != '':
            change = ''.join([change, ", ", key, "='", value, "'"])

    change = change[2:]

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the inputted products and change the data.
    for product in products:
        cursor.execute("""UPDATE information SET {c} WHERE product='{p}'""".\
            format(c=change, p=product))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeProduct(product, connection=None):
    """
    Remove a product tuple from the database.

    Args:
      products (str): The product to be removed from the database.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Convert to a valid string by adding or removing characters.
    product = "'" + product + "'"

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to remove the row of the given product.
    cursor.execute("""DELETE FROM information WHERE product={p}""".\
        format(p=product))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

"""
Hierarchy
"""
def addTitle(tier, title, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the title to the database.
    cursor.execute("""INSERT INTO hierarchy VALUES ('{tr}', '{te}')""".\
        format(tr=tier, te=title))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def setTitle(tier, oldTitle, newTitle, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""UPDATE hierarchy SET title='{te2}' WHERE tier='{tr}' AND
title='{te1}'""".format(tr=tier, te1=oldTitle, te2=newTitle))

    # Execute the statement to change any names in the information table.
    cursor.execute("""UPDATE information SET {t}='{nt}' WHERE {t}='{ot}'""".\
        format(t=tier, ot=oldTitle, nt=newTitle))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeTitle(tier, title, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""DELETE FROM hierarchy WHERE tier='{tr}' AND title='{te}'
""".format(tr=tier, te=title))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getTiers(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""SELECT DISTINCT tier FROM hierarchy""")

    # Fetch the returned data.
    tiers = [tier[0] for tier in cursor.fetchall()]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return tiers

def getForTier(tier, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""SELECT title FROM hierarchy WHERE tier='{t}'""".\
        format(t=tier))

    # Fetch the returned data.
    titles = [title[0] for title in cursor.fetchall()]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return titles

"""
Variable
"""
def addAlias(variable, alias, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the title to the database.
    cursor.execute("""INSERT INTO variable VALUES ('{v}', "{a}");""".\
        format(v=variable, a=alias.lower()))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def setAlias(variable, oldAlias, newAlias, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""UPDATE variable SET alias="{a2}" WHERE variable='{v}' AND
alias="{a1}";""".format(v=variable, a1=oldAlias, a2=newAlias))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeAlias(variable, alias, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""DELETE FROM variable WHERE variable='{v}' AND
alias="{a}";""".format(v=variable, a=alias))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getVariables(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""SELECT DISTINCT variable FROM variable""")

    # Fetch the returned data.
    variables = [variable[0] for variable in cursor.fetchall()]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return variables

def getForVariable(variable, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""SELECT alias FROM variable WHERE variable='{v}'""".\
        format(v=variable))

    # Fetch the returned data.
    aliases = [alias[0] for alias in cursor.fetchall()]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return aliases

def getVariableHash(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to remove the tier title combo from the database.
    cursor.execute("""SELECT alias, variable FROM variable""")

    # Fetch the returned data.
    lookup = {alias[0]: alias[1] for alias in cursor.fetchall()}

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return lookup

"""
Missing Products
"""
def addMissing(basis, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to add a missing product.
    cursor.execute("""INSERT OR IGNORE INTO missing (basis) VALUES ('{b}')""".\
        format(b=basis))

    # Execute the command to get the id of the input basis.
    cursor.execute("""SELECT id FROM missing WHERE basis='{b}'""".\
        format(b=basis))

    # Fetch the returned id.
    basisID = cursor.fetchone()[0]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return basisID

def getMissing(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to select all missing basis.
    cursor.execute("""SELECT id, basis FROM missing ORDER BY id""")

    # Fetch the returned data.
    missing = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return missing

def assignMissing(product, sku, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Call the command to update the information of the product.
    setProduct(product, {"sku": sku}, connection)

    # Execute the statement to get the ID of the basis.
    cursor.execute("""SELECT id FROM missing WHERE basis='{b}'""".\
        format(b=sku))

    # Fetch the ID.
    count = fetchone()[0]

    # Reassign the data stored to the proper product.
    idata.changeName("TEMP-" + count, product)

    # Execute the command to delete the sku from the missing list.
    cursor.execute("""DELETE FROM missing WHERE basis='{b}'""".format(b=sku))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

"""
Import Information
"""
def addImport(fileInfo, connection=None):
    """
    """

    # Put the inputs into the correct string form.
    columns = str(tuple(fileInfo.keys())).replace("'", '')
    values = str(tuple([x.encode() for x in fileInfo.values()]))

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the import information.
    cursor.execute("""INSERT INTO import {c} VALUES {v}""".format(c=columns,
        v=values))

    # Execute the statement to get the id of the input.
    cursor.execute("""SELECT id FROM import WHERE date_of_import='{doi}'""".\
        format(doi=fileInfo["date_of_import"]))

    # Fetch the returned id.
    importID = cursor.fetchone()[0]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return importID

"""
Link Products
"""
def addLink(old, new, connection=None):
    """
    """

    # Create the string form for the values.
    values = str((old, new))

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the link.
    cursor.execute("""INSERT OR REPLACE INTO link (old, new) VALUES {v}""".\
        format(v=values))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def setLink(old, new, kind, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the link.
    if kind == 1:
        cursor.execute("""UPDATE link SET old='{o}' WHERE new='{n}'""".\
            format(o=old, n=new))
    elif kind == 2:
        cursor.execute("""UPDATE link SET new='{n}' WHERE old='{o}'""".\
            format(o=old, n=new))
    else:
        cursor.execute("""UPDATE link SET old='{o}', new='{n}' WHERE
old='{o2}'""".format(o=old, n=new, o2=kind))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeLink(old, new, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to delete the input link.
    cursor.execute("""DELETE FROM link WHERE old='{o}' AND new='{n}'""".\
        format(o=old, n=new))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getLinks(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the link.
    cursor.execute("""SELECT old, new FROM link ORDER BY old""")

    # Fetch all of the returned data.
    links = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return links

def getLinksTo(product, connection=None):
    """
    Assumes links are one to one.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Initialize links.
    links = []

    # Execute the command to 
    cursor.execute("""SELECT old FROM link WHERE new='{n}'""".\
        format(n=product))

    # Fetch all of the returned data.
    links = [x[0] for x in cursor.fetchall()]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return links

"""
Helper Functions
"""
def text2date(text):
    """
    SQL text date format is yyyy-mm-dd.
    """

    # 
    return dt.date(int(text[0 : 4]), int(text[5 : 7]), int(text[8 : 10]))
