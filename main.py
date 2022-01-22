import mysql.connector as dbconn
import datetime

db = dbconn.connect(host="localhost", user="cs4430", passwd="Database4430!", db="northwind")
cursor = db.cursor()
# ------------------------------------------------------------------------------------------


def add_customer():
    print("ADD A CUSTOMER\n")
    sql = "INSERT INTO customers (customerid, companyname, contactname, contacttitle, address, city, region,  \
          postalcode, country, phone, fax) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cid = check_exist_cid()
    comp_name = input("CompanyName: ")
    contact_name = input("ContactName: ")
    cont_title = input("ContactTitle: ")
    address = input("Address: ")
    city = input("City: ")
    region = input("Region: ")
    postcode = input("PostalCode: ")
    country = input("Country: ")
    phone = input("Phone: ")
    fax = input("Fax: ")
    val = (cid, comp_name, contact_name, cont_title, address, city, region, postcode, country, phone, fax)
    cursor.execute(sql, val)
    db.commit()
    print("\nCustomer added!")
    main()


def add_order():
    print("ADD AN ORDER")
    oid = get_new_oid()
    add_order_table(oid)
    add_order_details_table(oid)


def add_order_table(oid):
    print("\nPlease add order details below.")

    cid, eid = check_cid_eid()
    orderdate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reqdate = get_req_date()
    shippeddate = None
    shipvia = check_shipvia()
    freight = float(input("Freight: "))
    freight = "{:.2f}".format(freight)
    shipname = input("ShipName: ")
    shipaddr = input("ShipAddress: ")
    shipcity = input("ShipCity: ")
    shipregion = input("ShipRegion: ")
    postcode = input("ShipPostalCode: ")
    shipcountry = input("ShipCountry: ")

    sql = "INSERT INTO orders (orderid, customerid, employeeid, orderdate, requireddate, shippeddate, shipvia, freight,\
     shipname, shipaddress, shipcity, shipregion, shippostalcode, shipcountry) VALUES \
     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (oid, cid, eid, orderdate, reqdate, shippeddate, shipvia, freight, shipname, shipaddr, shipcity, shipregion, postcode, shipcountry)
    cursor.execute(sql, val)
    db.commit()


def add_order_details_table(oid):
    print("\nPlease enter product details below.")
    productid = check_pid()
    sql = "SELECT discontinued, unitprice FROM products WHERE productid = %s"
    val = (productid, )
    cursor.execute(sql, val)
    for (dc, uprice) in cursor:
        if dc == 'y':
            print("\tSorry, this product has been discontinued!")
            get_add_prompt(oid)
        else:
            odid = get_new_odid()
            add_more_order_details(odid, oid, productid, uprice)
            get_add_prompt(oid)


def add_more_order_details(odid, oid, productid, uprice):
    print("UnitPrice of this product is", uprice)
    quantity = int(input("Quantity: "))
    discount = float(input("Discount: "))
    sql = "INSERT INTO order_details (id, orderid, productid, unitprice, quantity, discount) VALUES \
    (%s, %s, %s, %s, %s, %s)"
    val = (odid, oid, productid, uprice, quantity, discount)
    cursor.execute(sql, val)
    db.commit()


def remove_order():
    print("REMOVE AN ORDER\n")
    sql1 = "DELETE FROM orders WHERE orderid = %s"
    sql2 = "DELETE FROM order_details WHERE orderid = %s"
    orderid = check_oid()
    val = (orderid, )
    cursor.execute(sql2, val)
    cursor.execute(sql1, val)
    db.commit()
    print("\nOrder deleted!")
    main()


def ship_order():
    boolean_ship = True
    sql = "SELECT quantity, productid FROM order_details WHERE orderid = %s"
    orderid = check_oid()
    if check_shippeddate(orderid) is True:
        val = (orderid, )
        cursor.execute(sql, val)
        order_list = []
        for (quantity, productid) in cursor:
            order_list.append([productid, quantity])
        for pid, qty in order_list:
            sql = "SELECT unitsinstock, productid FROM products WHERE productid = %s"
            val = (pid, )
            cursor.execute(sql, val)
            for (unitsinstock, productid) in cursor:
                if boolean_ship is True:
                    if qty <= unitsinstock:
                        boolean_ship = True
                    else:
                        boolean_ship = False
                        print("\tNot enough units in stock to be shipped!")
                        break
        if boolean_ship is True:
            prompt_ship(orderid)
            for pid, qty in order_list:
                sql = "SELECT unitsinstock, productid FROM products WHERE productid = %s"
                val = (pid,)
                cursor.execute(sql, val)
                for (unitsinstock, productid) in cursor:
                    upd_unitsinstock(productid, qty)
            print("\nOrder shipped!")
    else:
        print("\tItem has already been shipped!")
    main()


def prompt_ship(oid):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    shipvia = check_shipvia()
    freight = float(input("Freight: "))
    freight = "{:.2f}".format(freight)
    sql = "UPDATE orders SET shippeddate = %s, shipvia = %s, freight = %s WHERE orderid = %s"
    val = (date, shipvia, freight, oid)
    cursor.execute(sql, val)
    db.commit()


def upd_unitsinstock(pid, qty):
    new_unitsinstock = 0
    sql = "SELECT unitsinstock, productid FROM products WHERE productid = %s"
    val = (pid,)
    cursor.execute(sql, val)
    for (unitsinstock, productid) in cursor:
        new_unitsinstock = unitsinstock - qty
    sql_upd = "UPDATE products SET unitsinstock = %s WHERE productid = %s"
    val_upd = (new_unitsinstock, pid)
    cursor.execute(sql_upd, val_upd)
    db.commit()


def print_pending():
    print("PRINT PENDING ORDERS\n")
    sql = "SELECT orderid, customerid, orderdate FROM orders WHERE shippeddate is NULL ORDER BY orderdate"
    f_str1 = "{:20s} | {:10s} | {:10s} | {:20s} | {:30s} | {:15s} | {:s}"
    f_str2 = "{:20s} | {:^10d} | {:10s} | {:20s} | {:30s} | {:15s} | {:s}"
    print(f_str1.format("OrderDate", "OrderID", "CustomerID", "ContactName", "CompanyName", "Country", "Phone"))
    cursor.execute(sql)
    order_list = []
    for (orderid, customerid, orderdate) in cursor:
        order_list.append([orderid, customerid, orderdate])

    for oid, cid, odate in order_list:
        cus_sql = "SELECT contactname, companyname, country, phone FROM customers where customerid = %s"
        val = (cid, )
        cursor.execute(cus_sql, val)
        for (cname, compname, country, phone) in cursor:
            cname = cname[:20]
            compname = compname[:30]
            country = country[:15]
            print(f_str2.format(str(odate), oid, cid, cname, compname, country, phone))
    main()


def restock():
    sql = "SELECT productid, unitsonorder, supplierid FROM products WHERE (unitsinstock + unitsonorder) < reorderlevel"
    cursor.execute(sql)
    restock_prod = []
    restock_prod_full = []
    print("ProductID of products that needs to be restocked: ")
    for (productid, unitsonorder, supplierid) in cursor:
        restock_prod.append(productid)
        restock_prod_full.append([productid, unitsonorder, supplierid])
        print(productid)
    if not restock_prod:
        print("\tNo products need to be restocked!")
        main()
    else:
        restock_prompt(restock_prod,restock_prod_full)


def restock_prompt(restock_prod, restock_prod_full):
    print("\nPlease enter details of the product you wish to restock.")
    product_ord = check_pid()
    while product_ord not in restock_prod:
        print("\tThis product does not need to be restocked, please enter a ProductID stated above")
        product_ord = check_pid()
    for item in restock_prod_full:
        pid = item[0]
        units = item[1]
        sid = item[2]
        if product_ord == pid:
            restock_qty = int(input("Please enter quantity you'd like to restock: "))
            new_qty = restock_qty + units
            sql = "UPDATE products SET unitsonorder = %s WHERE productid = %s"
            val = (new_qty, pid)
            cursor.execute(sql, val)
            print_supplier(sid)
            db.commit()
            print("\nItems restocked!")
    main()


def print_supplier(sid):
    print("\nSupplier Information: ")
    sql = "SELECT * FROM suppliers WHERE supplierid = %s"
    val = (sid, )
    cursor.execute(sql, val)
    for supplierid, companyname, contactname, contacttitle, address, city, region, postalcode, country, phone, fax,\
        homepage in cursor:
        print("\tSupplierID: ", supplierid)
        print("\tCompanyName: ", companyname)
        print("\tContactName: ", contactname)
        print("\tContactTitle: ", contacttitle)
        print("\tAddress: ", address)
        print("\tCity: ", city)
        print("\tRegion: ", region)
        print("\tPostalCode: ", postalcode)
        print("\tCountry: ", country)
        print("\tPhone: ", phone)
        print("\tFax: ", fax)
        print("\tHomepage: ", homepage)


def exit_program():
    print("Exiting program, thank you!")
# ------------------------------------------------------------------------------------------


def check_exist_cid():
    cid = input("CustomerID: ").upper()
    sql_cid = "SELECT customerid, phone FROM customers"
    cursor.execute(sql_cid)
    cid_list = []
    for (customerid, phone) in cursor:
        cid_list.append(customerid)
    while cid in cid_list:
        print("\tCustomerID already exists, please enter a new CID")
        cid = input("\tCustomerID: ").upper()
    final_cid = check_length_cid(cid)
    return final_cid


def check_length_cid(cid):
    if len(cid) > 5:
        cid = cid[:5]
        print("\tLength of CID too long, new CID is: ", cid)
        return cid
    else:
        return cid


def check_cid_eid():
    cid = input("CustomerID: ")
    sql_cid = "SELECT customerid,phone FROM customers"
    cursor.execute(sql_cid)
    cid_list = []
    for (customerid, phone) in cursor:
        cid_list.append(customerid)
    while cid.upper() not in cid_list:
        print("\tCustomerID does not exist, please enter valid CID")
        cid = input("\tCustomerID: ")

    eid = input("EmployeeID: ")
    sql_eid = "SELECT employeeid, lastname FROM employees"
    cursor.execute(sql_eid)
    eid_list = []
    for (employeeid, lastname) in cursor:
        eid_list.append(employeeid)
    while eid.isdigit() is False or int(eid) not in eid_list:
        print("\tEmployeeID does not exist, please enter valid EID")
        eid = input("\tEmployeeID: ")
    return cid.upper(), int(eid)


def get_req_date():
    print("\nPlease enter the date for which the products are required.")
    month = input("Please enter month: ")
    while month.isdigit() is False or int(month) < 1 or int(month) > 12:
        print("\tPlease enter valid month (1-12)!")
        month = input("\tPlease enter month: ")
    day = input("Please enter day: ")
    while day.isdigit() is False or int(day) < 1 or int(day) > 31:
        print("\tPlease enter valid day (1-31)!")
        day = input("\tPlease enter day: ")
    year = input("Please enter year: ")
    while year.isdigit() is False:
        print("\tPlease enter valid year in digits!")
        year = input("\tPlease enter year: ")
    date = datetime.datetime(int(year), int(month), int(day)).strftime('%Y-%m-%d %H:%M:%S')
    return date


def get_new_oid():
    oid = 0
    sql_getmax_oid = "SELECT MAX(orderid), MAX(id) FROM order_details"
    cursor.execute(sql_getmax_oid)
    for (maxoid, odid) in cursor:
        oid = maxoid + 1
    return oid


def get_new_odid():
    odid = 0
    sql_getmax_odid = "SELECT MAX(id), MAX(orderid) FROM order_details"
    cursor.execute(sql_getmax_odid)
    for (maxodid, orderid) in cursor:
        odid = maxodid + 1
    return odid


def check_pid():
    pid = input("ProductID: ")
    sql_pid = "SELECT productid, productname FROM products"
    cursor.execute(sql_pid)
    pid_list = []
    for (productid, productname) in cursor:
        pid_list.append(productid)
    while pid.isdigit() is False or int(pid) not in pid_list:
        print("\tProductID does not exist, please enter valid PID")
        pid = input("\tProductID: ")
    return int(pid)


def get_add_prompt(oid):
    add_prompt = input("Would you like to add another product? (y/n): ")
    if add_prompt[0].upper() == 'Y':
        add_order_details_table(oid)
    else:
        print("\nOrder succcessufully added! OrderID:",oid)
        main()


def check_oid():
    oid = input("OrderID: ")
    sql_oid = "SELECT orderid, customerid FROM orders"
    cursor.execute(sql_oid)
    oid_list = []
    for (orderid, customerid) in cursor:
        oid_list.append(orderid)
    while oid.isdigit() is False or int(oid) not in oid_list:
        print("\tOrderID does not exist, please enter valid OID")
        oid = input("\tOrderID: ")
    return int(oid)


def check_shippeddate(oid):
    sql = "SELECT shippeddate, orderid FROM orders WHERE orderid = %s"
    val = (oid, )
    cursor.execute(sql, val)
    for (shippeddate, orderid) in cursor:
        if shippeddate is None:
            return True
        else:
            return False


def check_shipvia():
    shipvia = input("Please enter ShipperID: ")
    while shipvia.isdigit() is False or int(shipvia) < 1 or int(shipvia) > 3:
        print("\tValue should be between 1-3")
        shipvia = input("\tPlease enter ShipperID: ")
    return int(shipvia)
# ------------------------------------------------------------------------------------------


def opening():
    print('''
    -------------------- MENU ------------------------
    1. Add a customer
    2. Add an order
    3. Remove an order
    4. Ship an order
    5. Print pending orders with customer information
    6. Restock products
    7. Exit
    ''')

    option = input("Please choose an option from the menu: ")
    while option.isdigit() is False or int(option) < 1 or int(option) > 7:
        print("\tPlease enter valid option!")
        option = input("\nPlease choose an option from the menu: ")
    print()
    return int(option)


def decide(option):
    if option == 1:
        add_customer()
    elif option == 2:
        add_order()
    elif option == 3:
        remove_order()
    elif option == 4:
        ship_order()
    elif option == 5:
        print_pending()
    elif option == 6:
        restock()
    elif option == 7:
        exit_program()


def main():
    option = opening()
    decide(option)


main()
cursor.close()
db.close()
