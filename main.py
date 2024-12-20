from flask import Flask, render_template, request, redirect, session, flash, url_for
from mysql.connector import connect, Error
from datetime import timedelta
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database connection function
def get_db_connection():
    try:
        connection = connect(
            host="localhost",
            user="root",
            password="Divya@2004",
            database="dm"  # Specify your database name here
        )
        return connection,connection.cursor(dictionary=True)
    except Error as e:
        print(f"Database connection error: {e}")
        return None,  None


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')
@app.route('/login', methods=['GET', 'POST'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection, cursor = get_db_connection()  # Get database connection and cursor
        
        if connection and cursor:  # Check if connection and cursor are valid
            try:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
                
                if user:
                    session['username'] = user['username']
                    session['user_id'] = user['id']
                    flash('Login successful!', 'success')
                    print(f"Redirecting to dashboard for user ID {session['user_id']}")
                    return redirect(url_for('dashboard'))  # Redirect to dashboard route
                else:
                    flash('Invalid credentials. Please try again.', 'error')
                    print(f"Invalid login attempt for username: {username}")
            except Error as e:
                print(f"Database error during login: {e}")
                flash('An error occurred during login. Please try again later.', 'error')
            finally:
                cursor.close()  # Ensure cursor is closed
                connection.close()  # Ensure connection is closed
        else:
            flash('Database connection failed', 'error')
    
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
     
    if 'username' in session:
        username = session.get('username')
        return render_template('dashboard.html', username=username)
    else:
        flash('You are not logged in. Please log in first.', 'error')
        return redirect(url_for('login'))

@app.route('/submit_details', methods=['POST'])
def submit_details():
    # Get form data
    name = request.form.get('name')
    dob = request.form.get('dob')
    email = request.form.get('email')
    phone = request.form.get('phone')
    role = request.form.get('role')
    
    # Validate input data
    if not name or not dob or not email or not phone or not role:
        return render_template('dashboard.html', message="All fields are required!", info_exists=False)

    # Store data in database
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO student_info (name, dob, email, phone, role) VALUES (%s, %s, %s, %s, %s)",
            (name, dob, email, phone, role)
        )
        mysql.connection.commit()
        return render_template('dashboard.html', message="Details submitted successfully!", info_exists=True, username=name)
    except Exception as e:
        print("Error inserting data into database:", e)
        return render_template('dashboard.html', message="There was an error, please try again.", info_exists=False)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        if not all([username, email, phone_number, password, confirm_password]):
            flash("All fields are required.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        else:
            connection, cursor = get_db_connection()
            if connection and cursor:  # Check if the connection and cursor are valid
                try:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                    user_exists = cursor.fetchone()
                    if user_exists:
                        flash("Username already taken.", "error")
                    else:
                        cursor.execute("INSERT INTO users (username, email, phone_number, password) VALUES (%s, %s, %s, %s)",
                                       (username, email, phone_number, password))
                        connection.commit()
                        flash("Account created successfully!", "success")
                        return redirect('/login')
                except Error as err:
                    flash(f"Database error: {err}", "error")
                finally:
                    cursor.close()
                    connection.close()
            else:
                flash("Database connection failed. Please try again later.", "error")

    return render_template('signup.html')

@app.route('/add_internship', methods=['GET', 'POST'])
def add_internship():
    if request.method == 'POST':
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Retrieve form data
                department = request.form.get('department')
                company_name = request.form.get('company')
                headquarters = request.form.get('headquarters')
                contact_number = request.form.get('contact_number')
                contact_email = request.form.get('contact_email')
                isocertified = request.form.get('isocertified') == 'on'
                ratings = request.form.get('ratings')
                base_fee = request.form.get('base_fee')

                # Insert company and internship information
                cursor.execute("INSERT INTO companies (name, headquarters, contact_number, contact_email, isocertified, ratings) VALUES (%s, %s, %s, %s, %s, %s)", 
                               (company_name, headquarters, contact_number, contact_email, isocertified, ratings))
                connection.commit()
                flash("Internship added successfully!", 'success')
            except Error as e:
                print(f"Database error while adding internship: {e}")
                flash("There was an issue adding the internship.", 'error')
            finally:
                cursor.close()
                connection.close()

    return render_template('add_internship.html')

@app.route('/view_cart')
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your cart.", "error")
        return redirect('/login')

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM cart WHERE user_id = %s", (user_id,))
            cart_items = cursor.fetchall()
            return render_template('cart.html', cart_items=cart_items)
        except Error as e:
            print(f"Error retrieving cart items: {e}")
            flash("Could not retrieve cart items.", "error")
        finally:
            cursor.close()
            connection.close()

    return redirect('/dashboard')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

@app.route('/help', methods=['GET', 'POST'])
def help():
    return render_template('help.html')

@app.route('/recommended_internships', methods=['GET'])
def recommended_internships():
    # Logic for recommended internships page
    return render_template('recommended_internships.html')



@app.route('/cart')
def cart():
    if 'username' not in session:
        flash('You are not logged in. Please log in first.', 'error')
        return redirect(url_for('login'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = """
            SELECT 
                i.id, 
                i.title, 
                c.name AS company, 
                i.location, 
                CASE 
                    WHEN i.paid = 1 THEN 'Yes' 
                    ELSE 'No' 
                END AS paid, 
                IFNULL(i.ratings, 'N/A') AS ratings 
            FROM cart crt
            INNER JOIN internships i ON crt.internship_id = i.id
            INNER JOIN companies c ON i.company_id = c.id
            WHERE crt.user_id = %s
        """
        cursor.execute(sql, (session['username'],))
        cart_items = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('An error occurred while fetching cart items.', 'error')
        cart_items = []

    return render_template('cart.html', cart_items=cart_items, username=session['username'])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash('You are not logged in. Please log in first.', 'error')
        return redirect(url_for('login'))

    username = session['username']

    try:
        # Get the database connection and cursor
        connection, mycursor = get_db_connection()
        if connection is None or mycursor is None:
            flash('Database connection failed.', 'error')
            return render_template('error.html')

        # Fetch user details including email, phone number, and joined date
        sql = "SELECT email, phone_number, joined_date, id FROM users WHERE username = %s"
        mycursor.execute(sql, (username,))
        user_details = mycursor.fetchone()

        if user_details:
            email = user_details['email'] if user_details['email'] is not None else 'N/A'
            phone_number = user_details['phone_number'] if user_details['phone_number'] is not None else 'N/A'
            joined_date = user_details['joined_date'].strftime('%d-%m-%Y') if user_details['joined_date'] is not None else 'N/A'
            user_id = user_details['id']  # Access user_id explicitly
        else:
            email = 'N/A'
            phone_number = 'N/A'
            joined_date = 'N/A'
            user_id = None

        # Fetch applied internships
        sql_internships = """
            SELECT 
                i.title, 
                c.name AS company, 
                i.location, 
                i.url, 
                CASE 
                    WHEN i.paid = 1 THEN 'Yes' 
                    ELSE 'No' 
                END AS paid, 
                CASE 
                    WHEN i.isocertified = 1 THEN 'Yes' 
                    ELSE 'No' 
                END AS isocertified, 
                i.ratings, 
                a.status
            FROM applied_internships a
            INNER JOIN internships i ON a.internship_id = i.id
            INNER JOIN companies c ON i.company_id = c.id
            WHERE a.user_id = %s
        """
        mycursor.execute(sql_internships, (user_id,))
        applied_internships = mycursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('An error occurred while fetching your profile information.', 'error')
        applied_internships = []
        email = 'N/A'
        phone_number = 'N/A'
        joined_date = 'N/A'
        user_id = None

    finally:
        if connection:
            connection.close()  # Ensure the connection is closed even if there's an error

    return render_template('profile.html', username=username, email=email, phone_number=phone_number, joined_date=joined_date, applied_internships=applied_internships)
@app.route('/filter_internships', methods=['POST'])
def filter_internships():
    # Get the filter criteria from the form
    filter_keyword = request.form.get('filterKeyword')
    filter_department = request.form.get('filterDepartment')
    filter_domain = request.form.get('filterDomain')
    filter_country = request.form.get('filterCountry')
    filter_state = request.form.get('filterState')
    filter_district = request.form.get('filterDistrict')
    filter_city = request.form.get('filterCity')
    filter_training_duration = request.form.get('filterTrainingDuration')
    filter_start_date = request.form.get('filterStartDate')
    filter_end_date = request.form.get('filterEndDate')
    filter_day_duration = request.form.get('filterDayDuration')
    filter_resume = request.form.get('filterResume')
    filter_paid_unpaid = request.form.get('filterPaidUnpaid')
    filter_fees = request.form.get('filterFees')

    # Build the query dynamically based on the filter criteria
    query = "SELECT * FROM internships WHERE 1=1"  # Starting query
    params = []  # Parameters for the query

    # Append conditions based on the form input
    if filter_keyword:
        query += " AND keyword LIKE %s"
        params.append(f"%{filter_keyword}%")  # Add % for partial matching

    if filter_department:
        query += " AND department LIKE %s"
        params.append(f"%{filter_department}%")

    if filter_domain:
        query += " AND domain LIKE %s"
        params.append(f"%{filter_domain}%")

    if filter_country:
        query += " AND country = %s"
        params.append(filter_country)

    if filter_state:
        query += " AND state = %s"
        params.append(filter_state)

    if filter_district:
        query += " AND district = %s"
        params.append(filter_district)

    if filter_city:
        query += " AND city = %s"
        params.append(filter_city)

    if filter_training_duration:
        query += " AND training_duration = %s"
        params.append(filter_training_duration)

    if filter_start_date:
        query += " AND start_date >= %s"
        params.append(filter_start_date)

    if filter_end_date:
        query += " AND end_date <= %s"
        params.append(filter_end_date)

    if filter_day_duration:
        query += " AND day_duration = %s"
        params.append(filter_day_duration)

    if filter_resume == 'yes':
        query += " AND resume_required = %s"
        params.append(1)  # Assuming 1 means resume required
    elif filter_resume == 'no':
        query += " AND resume_required = %s"
        params.append(0)  # Assuming 0 means no resume required

    if filter_paid_unpaid:
        query += " AND type = %s"
        params.append(filter_paid_unpaid)  # Assuming 'paid' or 'unpaid'

    if filter_fees:
        query += " AND fees <= %s"
        params.append(filter_fees)

    # Execute the query and fetch results using the params list
    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    internships = cursor.fetchall()

    # Pass the filtered internships to the template
    return render_template('view_internships.html', internships=internships)

@app.route('/logout')
def logout():
    session.clear()  # Clear the entire session
    flash('You have been logged out successfully.')
    return redirect('/login')

@app.route('/logout_confirmation')
def logout_confirmation():
    return render_template('logout_confirmation.html')

@app.route('/save_user_data', methods=['POST'])
def save_user_data():
    user_id = get_current_user_id()  # Function to get the logged-in user's ID
    data = request.get_json()
    
    # Save user data to the database
    save_user_info(user_id, data)  # Function to save user info in the database
    return jsonify(success=True)

@app.route('/internships')
def internships():
    if 'username' not in session:
        flash('You are not logged in. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Establish database connection
    mydb = mysql.connector.connect(**db_config)
    mycursor = mydb.cursor()

    sql = """
        SELECT 
            i.id, 
            i.title, 
            c.name AS company, 
            c.headquarters, 
            i.location, 
            c.contact_number, 
            c.contact_email, 
            CASE 
                WHEN i.paid = 1 THEN 'Yes' 
                ELSE 'No' 
            END AS paid, 
            CASE 
                WHEN c.isocertified = 1 THEN 'Yes' 
                ELSE 'No' 
            END AS isocertified, 
            IFNULL(i.ratings, 'N/A') AS ratings, 
            IFNULL(GROUP_CONCAT(CONCAT(f.duration, ': ', f.fee) SEPARATOR ', '), 'N/A') AS fees 
        FROM internships i
        INNER JOIN companies c ON i.company_id = c.id
        LEFT JOIN fees f ON i.id = f.internship_id
        GROUP BY i.id;
    """
    
    try:
        mycursor.execute(sql)
        internships = mycursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('An error occurred while fetching internships.', 'error')
        internships = []
    finally:
        mycursor.close()  # Close the cursor
        mydb.close()      # Close the database connection

    return render_template('internships.html', internships=internships, username=session['username'])

@app.route('/view_internship/<int:internship_id>')
def view_internship(internship_id):
    sql = """
        SELECT 
            i.title, 
            c.name AS company, 
            c.headquarters, 
            i.location, 
            c.contact_number, 
            c.contact_email, 
            CASE 
                WHEN i.paid = 1 THEN 'Yes' 
                ELSE 'No' 
            END AS paid, 
            CASE 
                WHEN c.isocertified = 1 THEN 'Yes' 
                ELSE 'No' 
            END AS isocertified, 
            i.ratings, 
            GROUP_CONCAT(CONCAT(f.duration, ': ', f.fee) SEPARATOR '<br>') AS fees 
        FROM internships i
        INNER JOIN companies c ON i.company_id = c.id
        LEFT JOIN fees f ON i.id = f.internship_id
        WHERE i.id = %s
        GROUP BY i.id
    """
    mycursor.execute(sql, (internship_id,))
    internship = mycursor.fetchone()

    if internship:
        return render_template('view_internship.html', internship=internship)
    else:
        flash('Internship not found.', 'error')
        return redirect(url_for('internships'))


@app.route('/check_user_info', methods=['GET'])
def check_user_info():
    user_id = get_current_user_id()  # Function to get the logged-in user's ID
    user_info = get_user_info(user_id)  # Function to fetch user info from the database

    # Check if user info exists
    if user_info:
        return jsonify(infoSubmitted=True)
    else:
        return jsonify(infoSubmitted=False)

if __name__ == '__main__':
    app.run(debug=True) 

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        # Perform search in the database
        sql = "SELECT * FROM internships WHERE title LIKE %s OR description LIKE %s"
        mycursor.execute(sql, ('%' + query + '%', '%' + query + '%'))
        results = mycursor.fetchall()
        return render_template('search_results.html', results=results, query=query)
    return render_template('search.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash('You are not logged in. Please log in first.', 'error')
        return redirect(url_for('login'))

    username = session['username']
    
    try:
        # Fetch user details including phone number and joined date
        sql = "SELECT email, phone_number, joined_date FROM users WHERE username = %s"
        mycursor.execute(sql, (username,))
        user_details = mycursor.fetchone()
        
        if user_details:
            email = user_details[0] if user_details[0] is not None else 'N/A'
            phone_number = user_details[1] if user_details[1] is not None else 'N/A'
            joined_date = user_details[2].strftime('%d-%m-%Y') if user_details[2] is not None else 'N/A'
        else:
            email = 'N/A'
            phone_number = 'N/A'
            joined_date = 'N/A'

        # Fetch applied internships
        sql_internships = """
            SELECT 
                i.title, 
                c.name AS company, 
                i.location, 
                i.url, 
                CASE 
                    WHEN i.paid = 1 THEN 'Yes' 
                    ELSE 'No' 
                END AS paid, 
                CASE 
                    WHEN i.isocertified = 1 THEN 'Yes' 
                    ELSE 'No' 
                END AS isocertified, 
                i.ratings, 
                a.status
            FROM applied_internships a
            INNER JOIN internships i ON a.internship_id = i.id
            INNER JOIN companies c ON i.company_id = c.id
            WHERE a.user_id = %s
        """
        mycursor.execute(sql_internships, (username,))
        applied_internships = mycursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('An error occurred while fetching your profile information.', 'error')
        applied_internships = []
        email = 'N/A'
        phone_number = 'N/A'
        joined_date = 'N/A'

    return render_template('profile.html', username=username, email=email, phone_number=phone_number, joined_date=joined_date, applied_internships=applied_internships)


if __name__ == "__main__":
    app.run(debug=True)
