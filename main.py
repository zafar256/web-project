# render template connects to html pages
from flask import Flask, render_template, request, redirect, flash, session, url_for


from functools import wraps
from flask_bcrypt import Bcrypt
from database import conn, cur  # import to connect to local database

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # connects flash


# ----------------------------------------------------------

# cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY, name VARCHAR ( 100 ) NOT NULL, buying_price NUMERIC(14, 2), selling_price NUMERIC(14, 2), stock_quantity INT DEFAULT 0);")
# cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY, pid int, quantity numeric(5,2), created_at TIMESTAMP, CONSTRAINT myproduct FOREIGN KEY(pid) references products(id) on UPDATE cascade on DELETE restrict);")
# cur.execute("CREATE TABLE IF NOT EXISTS purchases(id SERIAL PRIMARY KEY,  categoryid INT NOT NULL, description TEXT, amount DECIMAL(10,2) NOT NULL, purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, CONSTRAINT categoryid FOREIGN KEY (categoryid) REFERENCES categories(id) on UPDATE cascade on DELETE restrict);")
# cur.execute("CREATE TABLE IF NOT EXISTS stock (id serial PRIMARY KEY, pid int, quantity numeric(5,2), created_at TIMESTAMP, CONSTRAINT myproduct FOREIGN KEY(pid) references products(id) on UPDATE cascade on DELETE restrict);")
# cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email VARCHAR,password VARCHAR);")
# cur.execute("CREATE TABLE IF NOT EXISTS table categories (ID serial PRIMARY KEY, categoryname VARCHAR(100) NOT NULL);")

# conn.commit()


# ----------------------------------------------------------------


# decorative function

def login_required(f):
    @wraps(f)
    def protected(*args, **kwargs):
        if 'email' not in session:
            flash('You must first log in')
            next_url = request.url  # Store the requested URL
            return redirect(url_for('login', next=next_url))  # Pass next_url
        return f(*args, **kwargs)
    return protected
    
# ----------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ------------------------------------------------------------


@app.route("/dashboard")
@login_required
def dashboard():


    # today sales per product
    cur.execute("SELECT products.name, sum(sales.quantity*products.selling_price) from sales join products on products.id=sales.pid WHERE cast(created_at as DATE) = CURRENT_DATE group by products.name;")
    todaysalesperproduct = cur.fetchall()

    x = []
    y = []
    for i in todaysalesperproduct:
        x.append(i[0])
        y.append(float(i[1]))


    # today profit per product
    cur.execute("select products.name, sum(sales.quantity*(products.selling_price - products.buying_price )) from sales join products on products.id=sales.pid WHERE cast(created_at as DATE) = CURRENT_DATE group by products.name;")
    todayprofitsperproduct = cur.fetchall()

    pieproducts = []
    pieprofits = []
    for j in todayprofitsperproduct:
        pieproducts.append(j[0])
        pieprofits.append(float(j[1]))


    # general sales per product
    cur.execute("SELECT products.name, sum(sales.quantity*products.selling_price) from sales join products on products.id=sales.pid group by products.name;")
    salesperproduct = cur.fetchall()

    xx = []
    yy = []
    for i in salesperproduct:
        xx.append(i[0])
        yy.append(float(i[1]))

    # general profits per product
    cur.execute("select products.name, sum(sales.quantity*(products.selling_price - products.buying_price )) from sales join products on products.id=sales.pid group by products.name;")
    profitsperproduct = cur.fetchall()

    pieproducts2 = []
    pieprofits2 = []
    for j in profitsperproduct:
        pieproducts2.append(j[0])
        pieprofits2.append(float(j[1]))


    # Todays Net profits when all business expenses deducted

    # profits
    cur.execute("SELECT COALESCE(SUM(sales.quantity*(products.selling_price - products.buying_price )),0) FROM sales JOIN products on products.id=sales.pid WHERE cast(created_at as DATE) = CURRENT_DATE;")
    profits = cur.fetchone()
    print("-------rrtyy--t--r--e-", profits)
    todayprofit = int(profits[0])
    # expenses
    cur.execute("select COALESCE(sum(amount),0) from purchases where  cast(purchase_date as DATE) = CURRENT_DATE;")
    expenses = cur.fetchone()
    print("----thy----", expenses)
    todayexpenses = int(expenses[0])

    todaynetprofit = todayprofit - todayexpenses


    # General Net profits when all general business expenses deducted

    # profits
    cur.execute("SELECT COALESCE(SUM(sales.quantity*(products.selling_price - products.buying_price )),0) FROM sales JOIN products on products.id=sales.pid;")
    generalprofits = cur.fetchone()
    print("-------rrtyy--t--r--e-", profits)
    generalprofit = int(generalprofits[0])
    # expenses
    cur.execute("select COALESCE(sum(amount),0) from purchases;")
    generalexpense = cur.fetchone()
    print("----thy----", expenses)
    generalexpenses = int(generalexpense[0])

    generalnetprofit = generalprofit - generalexpenses


    # today expenses pie chart
    cur.execute("select purchases.categoryid, categories.categoryname, sum(purchases.amount) from purchases join categories on categories.id=purchases.categoryid WHERE cast(purchase_date as DATE) = CURRENT_DATE group by purchases.categoryid,categories.categoryname;")
    todayexpensespie = cur.fetchall()

    pieitem1 = []
    pieexpense1 = []
    for j in todayexpensespie:
        pieitem1.append(j[1])
        pieexpense1.append(float(j[2]))


    # general expenses pie chart
    cur.execute("select purchases.categoryid, categories.categoryname, sum(purchases.amount) from purchases join categories on categories.id=purchases.categoryid group by purchases.categoryid,categories.categoryname;;")
    generalexpensespie = cur.fetchall()

    print("----rthtt----eer---", generalexpensespie)

    pieitem = []
    pieexpense = []
    for j in generalexpensespie:
        pieitem.append(j[1])
        pieexpense.append(float(j[2]))


    # bar graph for total stock  

    cur.execute("select products.id as pid, products.name, sum(stock.quantity) from stock join products on stock.pid=products.id group by products.id, products.name;")
    totalstock = cur.fetchall()
    print("------stock----sss---", totalstock)

    xxx = []
    yyy = []
    for i in totalstock:
        xxx.append(i[1])
        yyy.append(float(i[2]))


    return render_template("dashboard.html", x=x, y=y, pieproducts=pieproducts, pieprofits=pieprofits, xx=xx, yy=yy, pieproducts2=pieproducts2, pieprofits2=pieprofits2, todaynetprofit=todaynetprofit, todayexpenses=todayexpenses, todayprofit=todayprofit, generalnetprofit=generalnetprofit, generalexpenses=generalexpenses, generalprofit=generalprofit, pieitem=pieitem, pieexpense=pieexpense, pieexpense1=pieexpense1, pieitem1=pieitem1, xxx=xxx, yyy=yyy)


# ---------------------------------------------------------------------------------



@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "GET":
        cur.execute("select * from products;")
        myproducts = cur.fetchall()
        return render_template("products.html", myproducts=myproducts)
    else:
        productname = request.form["productname"]
        buyingprice = float(request.form["buyingprice"])
        sellingprice = float(request.form["sellingprice"])

        queryinsert = "insert into products(name,buying_price,selling_price)"\
            "values('{}',{},{})".format(productname,
                                           buyingprice, sellingprice)
        

        cur.execute(queryinsert)
        conn.commit()
        return redirect('/products')      

# --------------

# route for editing products and expenses
# NB for updating the values passed in the request.form should match the entries in the database

@app.route("/updateproducts", methods=["POST"])
def updates():

    id = request.form["id"]
    name = request.form["name"]
    buyingprice = request.form["buying_price"]
    sellingprice = request.form["selling_price"]  

    queryupdateproducts = "UPDATE products SET name = '{}', buying_price = {}, selling_price = {} WHERE id = {}".format(
        name, buyingprice, sellingprice, id)
    cur.execute(queryupdateproducts)
    conn.commit()
    
    return redirect("/products")

# --------------------------------------------------------------------------===============---------------


@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    if request.method == "GET":
        cur.execute("select * from products;")
        products = cur.fetchall()
        cur.execute("select * from sales;")
        mysales = cur.fetchall()
        # print(products)
        return render_template("sales.html", mysales=mysales, products=products)
    else:
        pid = request.form["pid"]
        quantity = request.form["soldquantity"]
        querysalesinsert = "insert into sales(pid,quantity,created_at) "\
            "values({},{},now())".format(pid, quantity)
        cur.execute(querysalesinsert)
        conn.commit()
        return redirect("/sales")

# ---------------------------------------------------------------------------------------------------


@app.route("/stock", methods=["GET", "POST"])
@login_required
def stock():
    if request.method == "GET":
        cur.execute("select * from products;")
        products = cur.fetchall()
        cur.execute("select * from stock;")
        mystock = cur.fetchall()
        
        return render_template("stock.html", mystock=mystock, products=products)
    else:
        pid = request.form["pid"]
        quantity = request.form["availablequantity"]
        querystockinsert = "insert into stock(pid,quantity,created_at) "\
            "values({},{},now())".format(pid, quantity)
        cur.execute(querystockinsert)
        conn.commit()
        return redirect("/stock")

# ---------------------------------------------------------------------------------------------------


@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "GET":
        cur.execute("select * from purchases;")
        myexpenses = cur.fetchall()

        cur.execute("SELECT * FROM categories;")
        mycategories = cur.fetchall()  

        return render_template("expenses.html", myexpenses=myexpenses, mycategories=mycategories)

    else:
        expensecategory = request.form["categoryid"]
        description = request.form["description"]
        amount = float(request.form["amount"])      

        queryinsertexpense = "insert into purchases(categoryid,description,amount,purchase_date)"\
            "values('{}','{}',{},now())".format(expensecategory,
                                           description, amount)
        

        cur.execute(queryinsertexpense)
        conn.commit()
        return redirect('/expenses')

# -----------

@app.route("/updateexpenses", methods=["POST"])
def expenseupdate():

    id = request.form["id"]
    expense_category = request.form["categoryid"]
    expense_description = request.form["description"]
    expense_amount = request.form["amount"]  

    queryupdatexpense = "UPDATE purchases SET categoryid = '{}', description = '{}', amount = {} WHERE id = {}".format(
        expense_category, expense_description, expense_amount, id)
    cur.execute(queryupdatexpense)
    conn.commit()
    
    return redirect("/expenses")

# ----------------------------------------------------------------------------------------------------

@app.route("/expense_categories", methods=["GET", "POST"])
@login_required
def categories():
    if request.method == "GET":
        cur.execute("select * from categories;")
        mycategories = cur.fetchall()
        print("---------dcc----------cdcdcd----", mycategories)
        return render_template("categories.html", mycategories=mycategories)
    else:
        categoryname = request.form["categoryname"]

        queryinsertcategory = "insert into categories(categoryname)"\
            "values('{}')".format(categoryname)
        

        cur.execute(queryinsertcategory)
        conn.commit()
        return redirect('/expense_categories')

# -------------


@app.route("/updatecategories", methods=["POST"])
def categoryupdates():

    id = request.form["id"]
    # NB for updating the values passed in the request.form should match the entries in the database
    category_name = request.form["categoryname"]  

    queryupdatecategories = "UPDATE categories SET categoryname = '{}' WHERE id = {}".format(
        category_name, id)
    cur.execute(queryupdatecategories)
    conn.commit()
    
    return redirect("/expense_categories")

# ------------------------------------------------------------------------------------


# register route

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        cur.execute("select * from users;")
        users = cur.fetchall()
        return render_template("register.html", users=users)
    else:
        fullname = request.form["fullname"]
        email = request.form["email"]
        cur.execute("select id from users where email='{}'".format(email))
        email_exists = cur.fetchone()
  
        if not email_exists is None:
            flash('Email in use')
            return render_template("register.html")
        else:
            password = request.form["password"]
            comfirmpassword = request.form["comfirmpassword"]
            if comfirmpassword != password:
                flash('Passwords Dont Match')
                return redirect("/register")
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                queryregister = "insert into users(fullname,email,password) "\
                    "values('{}','{}','{}')".format(fullname, email, hashed_password)
                # .format includes the variables used
                cur.execute(queryregister)
                conn.commit()
                return redirect("/login")


# ------------------------------------------------------------------------------------
    

# login route

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get('next')  # Get next URL if provided
    print("---------hyghhyy---hhhhhh---", next_url)
    if request.method == "POST":
        emailaddress = request.form["email"]
        password = request.form["password"]
       
        cur.execute("select id from users where email='{}'".format(emailaddress))
        email_exists = cur.fetchone()
  
        if  email_exists is None:
            print("-----why not print-----")
            flash('Email does not exist. Try registering.')
            return redirect("/login")
        else:
            cur.execute("select password from users where email = '{}'".format(emailaddress))
            saved_hashed = cur.fetchone()[0]
            pass_bool = bcrypt.check_password_hash(saved_hashed, password)
            
            if pass_bool == False:
                flash("Invalid Credentials")
                return redirect("/login")
            else:
                print("-----ssdd--sdd--", request.form["next_url"])
                next_url = request.form["next_url"]
                session['email'] = emailaddress
                if next_url == "None":
                    return redirect("/dashboard")
                else:
                    url = "/"+next_url.split('/')[-1]
                    return redirect(url)
    return render_template("login.html", next_url=next_url)

# -------------------------------------------------------------------------------------------------------------  

@app.route("/forgotpassword")
def forgot():
    return render_template("forgotpassword.html") 

# -----------

@app.route("/resetpassword")
def reset():
    return render_template("resetpassword.html")      

# ----------------------------------------------------------------------------------------------------------
                 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------------------------------------------------------------------------------------


if __name__ == '__main__': 
    app.run(debug=True)
