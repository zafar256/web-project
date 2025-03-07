# render template connects to html pages
from flask import Flask, render_template, request, redirect, flash, session, url_for

from functools import wraps
from flask_bcrypt import Bcrypt
from database import conn, cur  # import to connect to local database

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # connects flash

# cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY, name VARCHAR ( 100 ) NOT NULL, buying_price NUMERIC(14, 2), selling_price NUMERIC(14, 2), stock_quantity INT DEFAULT 0);")
# cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY, pid int, quantity numeric(5,2), created_at TIMESTAMP, CONSTRAINT myproduct FOREIGN KEY(pid) references products(id) on UPDATE cascade on DELETE restrict);")
# conn.commit()

# decorative function
def login_required(f):
    @wraps(f)
    def protected():
        if 'email' not in session:
            return redirect(url_for('login'))
        return f()
    return protected
    

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    cur.execute("SELECT products.name, sum(sales.quantity*products.selling_price) from sales join products on products.id=sales.pid group by products.name;")
    salesperproduct = cur.fetchall()

    x = []
    y = []
    for i in salesperproduct:
        x.append(i[0])
        y.append(float(i[1]))

    cur.execute("select products.name, sum(sales.quantity*(products.selling_price - products.buying_price )) from sales join products on products.id=sales.pid group by products.name;")
    profits = cur.fetchall()

    pieproducts = []
    pieprofits = []
    for j in profits:
        pieproducts.append(j[0])
        pieprofits.append(float(j[1]))

    cur.execute("""
    WITH daily_sales AS (
        SELECT 
            SUM ((p.selling_price - p.buying_price) * s.quantity) AS sales, 
            s.created_at::DATE AS sale_date
        FROM 
            sales AS s
        JOIN 
            products AS p 
        ON 
            p.id = s.pid
        GROUP BY 
            s.created_at::DATE
    ),
    daily_expenses AS (
        SELECT 
            SUM(amount) AS total_expenses, 
            purchase_date::DATE AS expense_date
        FROM 
            purchases
        GROUP BY 
            purchase_date::DATE
    )
    SELECT 
        s.sale_date AS profit_date,
        COALESCE(s.sales, 0) - COALESCE(e.total_expenses, 0) AS final_profit
    FROM 
        daily_sales AS s
    FULL OUTER JOIN 
        daily_expenses AS e
    ON 
        s.sale_date = e.expense_date
    WHERE
        s.sale_date = '2025-03-07' OR e.expense_date = '2025-03-07'
    """)

    final_profit = cur.fetchone()
    print(final_profit)

    return render_template("dashboard.html", x=x, y=y, pieproducts=pieproducts, pieprofits=pieprofits)



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
        stockquantity = int(request.form["stockquantity"])

        queryinsert = "insert into products(name,buying_price,selling_price,stock_quantity)"\
            "values('{}',{},{},{})".format(productname,
                                           buyingprice, sellingprice, stockquantity)
        

        cur.execute(queryinsert)
        conn.commit()
        return redirect('/products')
    

@app.route("/contact-us")
def contact():
    return render_template("contact.html")


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

# route for editing products
# NB the values passed in the request.form should match the entries in the database

@app.route("/updateproducts", methods=["POST"])
def updates():

    id = request.form["id"]
    name = request.form["name"]
    buyingprice = request.form["buying_price"]
    sellingprice = request.form["selling_price"]
    quantity = request.form["stock_quantity"]

    queryupdateproducts = "UPDATE products SET name = '{}', buying_price = {}, selling_price = {}, stock_quantity = {} WHERE id = {}".format(
        name, buyingprice, sellingprice, quantity, id)
    cur.execute(queryupdateproducts)
    conn.commit()
    
    return redirect("/products")

# register route

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        cur.execute("select * from users;")
        users = cur.fetchall()
        # print(products)
        return render_template("register.html", users=users)
    else:
        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        queryregister = "insert into users(fullname,email,password) "\
            "values('{}','{}','{}')".format(fullname, email, password, hashed_password)
        # .format includes the variables used
        cur.execute(queryregister)
        conn.commit()
        return redirect("/register")
    

# login route

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emailaddress = request.form["email"]
        password = request.form["password"]

        querylogin = "select id from users where email = '{}' and password = '{}'".format(emailaddress,password)
        cur.execute(querylogin)

# row variable represents a single user
        row = cur.fetchone()
        if row is None:
            flash("Invalid Credentials")
            return render_template("login.html")
        else:
            session['email'] = emailaddress
            return redirect("/dashboard")
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == '__main__': 
    app.run(debug=True)
