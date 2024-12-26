import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import argparse
import logging
from datetime import datetime
from pathlib import Path
from tkcalendar import DateEntry


class PharmacyConfig:
    def __init__(self, server='LAPTOP-VIO2PNI9', database='project2', trusted_connection='yes', log_file='logs/pharmacy.log'):
        self.server = server
        self.database = database
        self.trusted_connection = trusted_connection
        self.log_file = log_file


class PharmacyManagementSystem:
    def __init__(self, root, config=None):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.state('zoomed')

        # Initialize config
        self.config = config or PharmacyConfig()

        # Setup logging
        self.setup_logging()

        # Database connection string
        self.conn_str = (
            'DRIVER={SQL Server};'
            f'SERVER={self.config.server};'
            f'DATABASE={self.config.database};'
            f'Trusted_Connection={self.config.trusted_connection};'
        )

        # Test database connection
        try:
            self.test_connection()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            raise

        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Initialize all tabs
        self.create_customers_tab()
        self.create_employees_tab()
        self.create_medications_tab()
        self.create_sales_tab()
        self.create_prescriptions_tab()
        self.create_stock_tab()
        self.create_suppliers_tab()
        self.create_address_dashboard_tab()
        self.create_monthly_orders_tab()
        self.create_monthly_sales_tab()

    def setup_logging(self):
        log_dir = Path(self.config.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Logging initialized.")

    def test_connection(self):
        try:
            with pyodbc.connect(self.conn_str) as conn:
                conn.cursor().execute("SELECT 1")
            logging.info("Database connection successful.")
        except pyodbc.Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    # -----------------------------
    # Customer Operations
    # -----------------------------
    def create_customers_tab(self):
        customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(customers_frame, text='Customers')

        # Form fields
        form_frame = ttk.LabelFrame(customers_frame, text="Customer Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Customer ID:", "cust_id"),
            ("Name:", "cust_name"),
            ("Phone:", "cust_phone"),
            ("Date of Birth:", "date_birth"),
            ("Gender:", "gender"),
            ("Insurance:", "insurance")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=idx//3, column=(idx%3)*2, padx=5, pady=5, sticky='w')
            if var_name in ["gender", "insurance"]:
                values = ['M', 'F'] if var_name == "gender" else ['YES', 'NO']
                combobox = ttk.Combobox(form_frame, values=values, state='readonly')
                combobox.grid(row=idx//3, column=(idx%3)*2 + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, combobox)
            elif var_name == "date_birth":
                date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                date_entry.grid(row=idx//3, column=(idx%3)*2 + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, date_entry)
            else:
                entry = ttk.Entry(form_frame)
                entry.grid(row=idx//3, column=(idx%3)*2 + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(customers_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Customer",
                   command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Customer",
                   command=self.update_customer).pack(side='left', padx=5)

        # Treeview for displaying customers
        tree_frame = ttk.Frame(customers_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Name', 'Phone', 'DOB', 'Gender', 'Insurance')
        self.customer_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=100, anchor='center')

        self.customer_tree.pack(fill='both', expand=True)
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.customer_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.customer_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_customers()

    def on_customer_select(self, event):
        selected_item = self.customer_tree.focus()
        if selected_item:
            values = self.customer_tree.item(selected_item, 'values')
            self.cust_id.delete(0, tk.END)
            self.cust_id.insert(0, values[0])
            self.cust_name.delete(0, tk.END)
            self.cust_name.insert(0, values[1])
            self.cust_phone.delete(0, tk.END)
            self.cust_phone.insert(0, values[2])
            self.date_birth.set_date(values[3])
            self.gender.set(values[4])
            self.insurance.set(values[5])

    def load_customers(self):
        query = """
        SELECT cust_id, cust_name, cust_phone, date_birth, 
               gender, insurance
        FROM Customer
        """
        customers = self.execute_db_operation(query)
        self.customer_tree.delete(*self.customer_tree.get_children())
        if customers:
            for customer in customers:
                cust_date = customer.date_birth.strftime('%Y-%m-%d') if isinstance(customer.date_birth, datetime) else customer.date_birth
                self.customer_tree.insert('', 'end', values=(customer.cust_id, customer.cust_name, customer.cust_phone, cust_date, customer.gender, customer.insurance))

    def add_customer(self):
        try:
            cust_id = self.cust_id.get().strip()
            cust_name = self.cust_name.get().strip()
            cust_phone = self.cust_phone.get().strip()
            date_birth = self.date_birth.get_date().strftime('%Y-%m-%d')
            gender = self.gender.get()
            insurance = self.insurance.get()

            if not cust_id or not cust_name:
                messagebox.showerror("Error", "Please enter Customer ID and Name.")
                return

            query = """
            INSERT INTO Customer (cust_id, cust_name, cust_phone, date_birth, 
                                  gender, insurance)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                cust_id,
                cust_name,
                cust_phone,
                date_birth,
                gender,
                insurance
            )
            self.execute_db_operation(query, params)
            self.load_customers()
            messagebox.showinfo("Success", "Customer added successfully!")
            self.clear_customer_form()
            logging.info(f"Added customer: {cust_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding customer: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding customer: {str(e)}")
            logging.error(f"Error adding customer: {e}")

    def update_customer(self):
        try:
            cust_id = self.cust_id.get().strip()
            cust_name = self.cust_name.get().strip()
            cust_phone = self.cust_phone.get().strip()
            date_birth = self.date_birth.get_date().strftime('%Y-%m-%d')
            gender = self.gender.get()
            insurance = self.insurance.get()

            if not cust_id:
                messagebox.showerror("Error", "Please enter Customer ID.")
                return

            query = """
            UPDATE Customer
            SET cust_name = ?, cust_phone = ?, date_birth = ?, 
                gender = ?, insurance = ?
            WHERE cust_id = ?
            """
            params = (
                cust_name,
                cust_phone,
                date_birth,
                gender,
                insurance,
                cust_id
            )
            self.execute_db_operation(query, params)
            self.load_customers()
            messagebox.showinfo("Success", "Customer updated successfully!")
            self.clear_customer_form()
            logging.info(f"Updated customer: {cust_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating customer: {str(e)}")
            logging.error(f"Error updating customer: {e}")

    def clear_customer_form(self):
        self.cust_id.delete(0, tk.END)
        self.cust_name.delete(0, tk.END)
        self.cust_phone.delete(0, tk.END)
        self.date_birth.set_date(datetime.today())
        self.gender.set('')
        self.insurance.set('')

    # -----------------------------
    # Employee Operations
    # -----------------------------
    def create_employees_tab(self):
        employees_frame = ttk.Frame(self.notebook)
        self.notebook.add(employees_frame, text='Employees')

        # Form fields
        form_frame = ttk.LabelFrame(employees_frame, text="Employee Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Employee ID:", "emp_id"),
            ("Title:", "emp_title"),
            ("Name:", "emp_name"),
            ("Phone:", "emp_phone"),
            ("Date of Birth:", "emp_dob"),
            ("Gender:", "emp_gender"),
            ("Hire Date:", "hire_date"),
            ("Salary:", "salary")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            row = idx // 4
            col = (idx % 4) * 2
            ttk.Label(form_frame, text=label_text).grid(row=row, column=col, padx=5, pady=5, sticky='w')
            if var_name in ["emp_gender"]:
                combobox = ttk.Combobox(form_frame, values=['M', 'F'], state='readonly')
                combobox.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, combobox)
            elif var_name in ["emp_dob", "hire_date"]:
                date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                date_entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, date_entry)
            else:
                entry = ttk.Entry(form_frame)
                entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(employees_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Employee",
                   command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Employee",
                   command=self.update_employee).pack(side='left', padx=5)

        # Treeview for displaying employees
        tree_frame = ttk.Frame(employees_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Title', 'Name', 'Phone', 'DOB', 'Gender', 'Hire Date', 'Salary')
        self.employee_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=100, anchor='center')

        self.employee_tree.pack(fill='both', expand=True)
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.employee_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.employee_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_employees()

    def on_employee_select(self, event):
        selected_item = self.employee_tree.focus()
        if selected_item:
            values = self.employee_tree.item(selected_item, 'values')
            self.emp_id.delete(0, tk.END)
            self.emp_id.insert(0, values[0])
            self.emp_title.delete(0, tk.END)
            self.emp_title.insert(0, values[1])
            self.emp_name.delete(0, tk.END)
            self.emp_name.insert(0, values[2])
            self.emp_phone.delete(0, tk.END)
            self.emp_phone.insert(0, values[3])
            self.emp_dob.set_date(values[4])
            self.emp_gender.set(values[5])
            self.hire_date.set_date(values[6])
            self.salary.delete(0, tk.END)
            self.salary.insert(0, values[7])

    def load_employees(self):
        query = """
        SELECT emp_id, title, emp_name, emp_phone, date_birth, 
               gender, hire_date, salary
        FROM Employee
        """
        employees = self.execute_db_operation(query)
        self.employee_tree.delete(*self.employee_tree.get_children())
        if employees:
            for employee in employees:
                emp_dob = employee.date_birth.strftime('%Y-%m-%d') if isinstance(employee.date_birth, datetime) else employee.date_birth
                hire_date = employee.hire_date.strftime('%Y-%m-%d') if isinstance(employee.hire_date, datetime) else employee.hire_date
                self.employee_tree.insert('', 'end', values=(employee.emp_id, employee.title, employee.emp_name, employee.emp_phone, emp_dob, employee.gender, hire_date, f"{employee.salary:.2f}"))

    def add_employee(self):
        try:
            emp_id = self.emp_id.get().strip()
            emp_title = self.emp_title.get().strip()
            emp_name = self.emp_name.get().strip()
            emp_phone = self.emp_phone.get().strip()
            emp_dob = self.emp_dob.get_date().strftime('%Y-%m-%d')
            emp_gender = self.emp_gender.get()
            hire_date = self.hire_date.get_date().strftime('%Y-%m-%d')
            salary = self.salary.get().strip()

            if not emp_id or not emp_name:
                messagebox.showerror("Error", "Please enter Employee ID and Name.")
                return

            if not self.is_valid_float(salary):
                messagebox.showerror("Error", "Salary must be a number.")
                return

            query = """
            INSERT INTO Employee (emp_id, title, emp_name, emp_phone, date_birth,
                                  gender, hire_date, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                emp_id,
                emp_title,
                emp_name,
                emp_phone,
                emp_dob,
                emp_gender,
                hire_date,
                float(salary)
            )
            self.execute_db_operation(query, params)
            self.load_employees()
            messagebox.showinfo("Success", "Employee added successfully!")
            self.clear_employee_form()
            logging.info(f"Added employee: {emp_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding employee: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding employee: {str(e)}")
            logging.error(f"Error adding employee: {e}")

    def update_employee(self):
        try:
            emp_id = self.emp_id.get().strip()
            emp_title = self.emp_title.get().strip()
            emp_name = self.emp_name.get().strip()
            emp_phone = self.emp_phone.get().strip()
            emp_dob = self.emp_dob.get_date().strftime('%Y-%m-%d')
            emp_gender = self.emp_gender.get()
            hire_date = self.hire_date.get_date().strftime('%Y-%m-%d')
            salary = self.salary.get().strip()

            if not emp_id:
                messagebox.showerror("Error", "Please enter Employee ID.")
                return

            if not self.is_valid_float(salary):
                messagebox.showerror("Error", "Salary must be a number.")
                return

            query = """
            UPDATE Employee
            SET title = ?, emp_name = ?, emp_phone = ?, date_birth = ?, 
                gender = ?, hire_date = ?, salary = ?
            WHERE emp_id = ?
            """
            params = (
                emp_title,
                emp_name,
                emp_phone,
                emp_dob,
                emp_gender,
                hire_date,
                float(salary),
                emp_id
            )
            self.execute_db_operation(query, params)
            self.load_employees()
            messagebox.showinfo("Success", "Employee updated successfully!")
            self.clear_employee_form()
            logging.info(f"Updated employee: {emp_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating employee: {str(e)}")
            logging.error(f"Error updating employee: {e}")

    def clear_employee_form(self):
        self.emp_id.delete(0, tk.END)
        self.emp_title.delete(0, tk.END)
        self.emp_name.delete(0, tk.END)
        self.emp_phone.delete(0, tk.END)
        self.emp_dob.set_date(datetime.today())
        self.emp_gender.set('')
        self.hire_date.set_date(datetime.today())
        self.salary.delete(0, tk.END)

    def is_valid_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    # -----------------------------
    # Medications Operations
    # -----------------------------
    def create_medications_tab(self):
        medications_frame = ttk.Frame(self.notebook)
        self.notebook.add(medications_frame, text='Medications')

        # Form fields
        form_frame = ttk.LabelFrame(medications_frame, text="Medication Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Medication ID:", "med_id"),
            ("Name:", "med_name"),
            ("Manufacturer:", "manufacturer"),
            ("Price:", "med_price"),
            ("Quantity:", "med_quantity")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=idx//3, column=(idx%3)*2, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(form_frame)
            entry.grid(row=idx//3, column=(idx%3)*2 + 1, padx=5, pady=5, sticky='w')
            setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(medications_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Medication",
                   command=self.add_medication).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Medication",
                   command=self.update_medication).pack(side='left', padx=5)

        # Treeview
        tree_frame = ttk.Frame(medications_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Name', 'Manufacturer', 'Price', 'Quantity')
        self.medication_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.medication_tree.heading(col, text=col)
            self.medication_tree.column(col, width=100, anchor='center')

        self.medication_tree.pack(fill='both', expand=True)
        self.medication_tree.bind('<<TreeviewSelect>>', self.on_medication_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.medication_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.medication_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_medications()

    def on_medication_select(self, event):
        selected_item = self.medication_tree.focus()
        if selected_item:
            values = self.medication_tree.item(selected_item, 'values')
            self.med_id.delete(0, tk.END)
            self.med_id.insert(0, values[0])
            self.med_name.delete(0, tk.END)
            self.med_name.insert(0, values[1])
            self.manufacturer.delete(0, tk.END)
            self.manufacturer.insert(0, values[2])
            self.med_price.delete(0, tk.END)
            self.med_price.insert(0, values[3])
            self.med_quantity.delete(0, tk.END)
            self.med_quantity.insert(0, values[4])

    def load_medications(self):
        query = """
        SELECT med_id, med_name, manufacture, price, med_quantity
        FROM Medication
        """
        medications = self.execute_db_operation(query)
        self.medication_tree.delete(*self.medication_tree.get_children())
        if medications:
            for med in medications:
                self.medication_tree.insert('', 'end', values=(med.med_id, med.med_name, med.manufacture, f"{med.price:.2f}", med.med_quantity))

    def add_medication(self):
        try:
            med_id = self.med_id.get().strip()
            med_name = self.med_name.get().strip()
            manufacturer = self.manufacturer.get().strip()
            price = self.med_price.get().strip()
            quantity = self.med_quantity.get().strip()

            if not med_id or not med_name:
                messagebox.showerror("Error", "Please enter Medication ID and Name.")
                return

            if not self.is_valid_float(price) or not quantity.isdigit():
                messagebox.showerror("Error", "Price must be a number and Quantity must be an integer.")
                return

            query = """
            INSERT INTO Medication (med_id, med_name, manufacture, price, med_quantity)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (
                med_id,
                med_name,
                manufacturer,
                float(price),
                int(quantity)
            )
            self.execute_db_operation(query, params)
            self.load_medications()
            messagebox.showinfo("Success", "Medication added successfully!")
            self.clear_medication_form()
            logging.info(f"Added medication: {med_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding medication: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding medication: {str(e)}")
            logging.error(f"Error adding medication: {e}")

    def update_medication(self):
        try:
            med_id = self.med_id.get().strip()
            med_name = self.med_name.get().strip()
            manufacturer = self.manufacturer.get().strip()
            price = self.med_price.get().strip()
            quantity = self.med_quantity.get().strip()

            if not med_id:
                messagebox.showerror("Error", "Please enter Medication ID.")
                return

            if not self.is_valid_float(price) or not quantity.isdigit():
                messagebox.showerror("Error", "Price must be a number and Quantity must be an integer.")
                return

            query = """
            UPDATE Medication
            SET med_name = ?, manufacture = ?, price = ?, med_quantity = ?
            WHERE med_id = ?
            """
            params = (
                med_name,
                manufacturer,
                float(price),
                int(quantity),
                med_id
            )
            self.execute_db_operation(query, params)
            self.load_medications()
            messagebox.showinfo("Success", "Medication updated successfully!")
            self.clear_medication_form()
            logging.info(f"Updated medication: {med_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating medication: {str(e)}")
            logging.error(f"Error updating medication: {e}")

    def clear_medication_form(self):
        self.med_id.delete(0, tk.END)
        self.med_name.delete(0, tk.END)
        self.manufacturer.delete(0, tk.END)
        self.med_price.delete(0, tk.END)
        self.med_quantity.delete(0, tk.END)

    # -----------------------------
    # Sales Operations
    # -----------------------------
    def create_sales_tab(self):
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text='Sales')

        # Sales form
        form_frame = ttk.LabelFrame(sales_frame, text="Sale Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Sale ID:", "sale_id"),
            ("Customer ID:", "sale_cust_id"),
            ("Employee ID:", "sale_emp_id"),
            ("Sale Type:", "sale_type"),
            ("Payment Method:", "payment_method"),
            ("Sale Date:", "sale_date")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            row = idx // 3
            col = (idx % 3) * 2
            ttk.Label(form_frame, text=label_text).grid(row=row, column=col, padx=5, pady=5, sticky='w')
            if var_name == "sale_type":
                combobox = ttk.Combobox(form_frame, values=['pickup', 'delivery'], state='readonly')
                combobox.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, combobox)
            elif var_name == "payment_method":
                combobox = ttk.Combobox(form_frame, values=['CASH', 'VISA', 'INSURANCE'], state='readonly')
                combobox.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, combobox)
            elif var_name == "sale_date":
                date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                date_entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, date_entry)
            else:
                entry = ttk.Entry(form_frame)
                entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, entry)

        # Sale Details Frame
        details_frame = ttk.LabelFrame(sales_frame, text="Sale Items", padding=10)
        details_frame.pack(fill='x', padx=10, pady=5)

        sale_item_fields = [
            ("Medication ID:", "sale_med_id"),
            ("Quantity:", "sale_quantity")
        ]

        for idx, (label_text, var_name) in enumerate(sale_item_fields):
            ttk.Label(details_frame, text=label_text).grid(row=0, column=idx*2, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(details_frame)
            entry.grid(row=0, column=idx*2 + 1, padx=5, pady=5, sticky='w')
            setattr(self, var_name, entry)

        ttk.Button(details_frame, text="Add Item",
                   command=self.add_sale_item).grid(row=0, column=4, padx=5, pady=5, sticky='w')

        # Sale Items Treeview
        columns = ('Medication ID', 'Name', 'Unit Price', 'Quantity', 'Total')
        self.sales_details_tree = ttk.Treeview(details_frame, columns=columns, show='headings')
        for col in columns:
            self.sales_details_tree.heading(col, text=col)
            self.sales_details_tree.column(col, width=100, anchor='center')

        self.sales_details_tree.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky='nsew')

        # Add scrollbar
        scrollbar_details = ttk.Scrollbar(details_frame, orient='vertical',
                                          command=self.sales_details_tree.yview)
        scrollbar_details.grid(row=1, column=5, sticky='ns')
        self.sales_details_tree.configure(yscrollcommand=scrollbar_details.set)

        # Sale Total Label
        self.sale_total_label = ttk.Label(sales_frame, text="Total: $0.00", font=('Arial', 12))
        self.sale_total_label.pack(pady=5)

        # Buttons
        btn_frame = ttk.Frame(sales_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Complete Sale",
                   command=self.complete_sale).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel Sale",
                   command=self.cancel_sale).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Sale",
                   command=self.delete_sale).pack(side='left', padx=5)

        # Sales Treeview
        tree_frame = ttk.Frame(sales_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns_sales = ('ID', 'Customer', 'Employee', 'Type',
                         'Payment', 'Date', 'Total')
        self.sales_tree = ttk.Treeview(tree_frame, columns=columns_sales, show='headings')
        for col in columns_sales:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100, anchor='center')

        self.sales_tree.pack(fill='both', expand=True)
        self.sales_tree.bind('<<TreeviewSelect>>', self.on_sale_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.sales_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.sales_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_sales()
        self.current_sale_total = 0.0

    def add_sale_item(self):
        med_id = self.sale_med_id.get().strip()
        quantity = self.sale_quantity.get().strip()
        if not med_id or not quantity:
            messagebox.showerror("Error", "Please enter Medication ID and Quantity.")
            return
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return

        query = """
        SELECT med_name, price, med_quantity
        FROM Medication
        WHERE med_id = ?
        """
        result = self.execute_db_operation(query, (med_id,))
        if not result:
            messagebox.showerror("Error", "Medication ID not found.")
            return
        med_name, unit_price, available_qty = result[0]
        if quantity > available_qty:
            messagebox.showerror("Error", f"Only {available_qty} units available.")
            return
        total_price = float(unit_price) * quantity
        self.sales_details_tree.insert('', 'end', values=(med_id, med_name, f"{unit_price:.2f}", quantity, f"{total_price:.2f}"))
        self.current_sale_total += total_price
        self.sale_total_label.config(text=f"Total: ${self.current_sale_total:.2f}")
        self.sale_med_id.delete(0, tk.END)
        self.sale_quantity.delete(0, tk.END)

    def complete_sale(self):
        sale_id = self.sale_id.get().strip()
        cust_id = self.sale_cust_id.get().strip()
        emp_id = self.sale_emp_id.get().strip()
        sale_type = self.sale_type.get()
        payment_method = self.payment_method.get()
        sale_date = self.sale_date.get_date().strftime('%Y-%m-%d')

        if not sale_id or not cust_id or not emp_id or not sale_type or not payment_method:
            messagebox.showerror("Error", "Please fill in all sale details.")
            return
        if not self.sales_details_tree.get_children():
            messagebox.showerror("Error", "No sale items added.")
            return

        try:
            # Insert into Sales table
            query_sales = """
            INSERT INTO Sales (sale_id, cust_id, emp_id, sale_type, payment_method, sale_date, sale_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params_sales = (
                sale_id,
                cust_id,
                emp_id,
                sale_type,
                payment_method,
                sale_date,
                self.current_sale_total
            )
            self.execute_db_operation(query_sales, params_sales)

            # Insert into Sales_Details table and update Medication quantity
            for child in self.sales_details_tree.get_children():
                med_id, _, unit_price, quantity, total = self.sales_details_tree.item(child, 'values')
                query_details = """
                INSERT INTO Sales_Details (sale_id, med_id, unit_price, sell_quantity, total)
                VALUES (?, ?, ?, ?, ?)
                """
                params_details = (
                    sale_id,
                    med_id,
                    float(unit_price),
                    int(quantity),
                    float(total)
                )
                self.execute_db_operation(query_details, params_details)

                # Update Medication quantity
                query_update = """
                UPDATE Medication
                SET med_quantity = med_quantity - ?
                WHERE med_id = ?
                """
                self.execute_db_operation(query_update, (int(quantity), med_id))

            self.load_sales()
            self.sales_details_tree.delete(*self.sales_details_tree.get_children())
            self.sale_total_label.config(text="Total: $0.00")
            self.current_sale_total = 0.0
            messagebox.showinfo("Success", "Sale completed successfully!")
            self.clear_sale_form()
            logging.info(f"Completed sale: {sale_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while completing sale: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error completing sale: {str(e)}")
            logging.error(f"Error completing sale: {e}")

    def cancel_sale(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this sale?"):
            self.sales_details_tree.delete(*self.sales_details_tree.get_children())
            self.sale_total_label.config(text="Total: $0.00")
            self.current_sale_total = 0.0
            self.clear_sale_form()
            logging.info("Sale canceled.")

    def delete_sale(self):
        sale_id = self.sale_id.get().strip()
        if not sale_id:
            messagebox.showerror("Error", "Please enter Sale ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this sale?"):
            try:
                # Retrieve sale items to restore medication quantities
                query_items = """
                SELECT med_id, sell_quantity
                FROM Sales_Details
                WHERE sale_id = ?
                """
                sale_items = self.execute_db_operation(query_items, (sale_id,))
                if sale_items:
                    for med_id, quantity in sale_items:
                        query_restore = """
                        UPDATE Medication
                        SET med_quantity = med_quantity + ?
                        WHERE med_id = ?
                        """
                        self.execute_db_operation(query_restore, (int(quantity), med_id))

                # Delete from Sales_Details
                query_details = "DELETE FROM Sales_Details WHERE sale_id = ?"
                self.execute_db_operation(query_details, (sale_id,))

                # Delete from Sales
                query_sales = "DELETE FROM Sales WHERE sale_id = ?"
                self.execute_db_operation(query_sales, (sale_id,))

                self.load_sales()
                messagebox.showinfo("Success", "Sale deleted successfully!")
                self.clear_sale_form()
                logging.info(f"Deleted sale: {sale_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting sale: {str(e)}")
                logging.error(f"Error deleting sale: {e}")

    def clear_sale_form(self):
        self.sale_id.delete(0, tk.END)
        self.sale_cust_id.delete(0, tk.END)
        self.sale_emp_id.delete(0, tk.END)
        self.sale_type.set('')
        self.payment_method.set('')
        self.sale_date.set_date(datetime.today())

    def load_sales(self):
        query = """
        SELECT sale_id, cust_id, emp_id, sale_type, payment_method, sale_date, sale_total
        FROM Sales
        """
        sales = self.execute_db_operation(query)
        self.sales_tree.delete(*self.sales_tree.get_children())
        if sales:
            for sale in sales:
                sale_date = sale.sale_date.strftime('%Y-%m-%d') if isinstance(sale.sale_date, datetime) else sale.sale_date
                self.sales_tree.insert('', 'end', values=(sale.sale_id, sale.cust_id, sale.emp_id, sale.sale_type, sale.payment_method, sale_date, f"{sale.sale_total:.2f}"))

    def on_sale_select(self, event):
        selected_item = self.sales_tree.focus()
        if selected_item:
            values = self.sales_tree.item(selected_item, 'values')
            self.sale_id.delete(0, tk.END)
            self.sale_id.insert(0, values[0])
            self.sale_cust_id.delete(0, tk.END)
            self.sale_cust_id.insert(0, values[1])
            self.sale_emp_id.delete(0, tk.END)
            self.sale_emp_id.insert(0, values[2])
            self.sale_type.set(values[3])
            self.payment_method.set(values[4])
            self.sale_date.set_date(values[5])
            self.current_sale_total = float(values[6])
            self.sale_total_label.config(text=f"Total: ${self.current_sale_total:.2f}")

    # -----------------------------
    # Prescriptions Operations
    # -----------------------------
    def create_prescriptions_tab(self):
        prescriptions_frame = ttk.Frame(self.notebook)
        self.notebook.add(prescriptions_frame, text='Prescriptions')

        # Form fields
        form_frame = ttk.LabelFrame(prescriptions_frame, text="Prescription Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Prescription ID:", "presc_id"),
            ("Customer ID:", "presc_cust_id"),
            ("Doctor:", "presc_doctor"),
            ("Issue Date:", "presc_issue_date")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            row = idx // 2
            col = (idx % 2) * 2
            ttk.Label(form_frame, text=label_text).grid(row=row, column=col, padx=5, pady=5, sticky='w')
            if var_name == "presc_issue_date":
                date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                date_entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, date_entry)
            else:
                entry = ttk.Entry(form_frame)
                entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(prescriptions_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Prescription",
                   command=self.add_prescription).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Prescription",
                   command=self.update_prescription).pack(side='left', padx=5)

        # Treeview for displaying prescriptions
        tree_frame = ttk.Frame(prescriptions_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Customer', 'Doctor', 'Issue Date')
        self.prescription_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.prescription_tree.heading(col, text=col)
            self.prescription_tree.column(col, width=150, anchor='center')

        self.prescription_tree.pack(fill='both', expand=True)
        self.prescription_tree.bind('<<TreeviewSelect>>', self.on_prescription_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.prescription_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.prescription_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_prescriptions()

    def on_prescription_select(self, event):
        selected_item = self.prescription_tree.focus()
        if selected_item:
            values = self.prescription_tree.item(selected_item, 'values')
            self.presc_id.delete(0, tk.END)
            self.presc_id.insert(0, values[0])
            self.presc_cust_id.delete(0, tk.END)
            self.presc_cust_id.insert(0, values[1])
            self.presc_doctor.delete(0, tk.END)
            self.presc_doctor.insert(0, values[2])
            self.presc_issue_date.set_date(values[3])

    def load_prescriptions(self):
        query = """
        SELECT p_id, cust_id, doctor, p_issue_date
        FROM Prescription
        """
        prescriptions = self.execute_db_operation(query)
        self.prescription_tree.delete(*self.prescription_tree.get_children())
        if prescriptions:
            for presc in prescriptions:
                issue_date = presc.p_issue_date.strftime('%Y-%m-%d') if isinstance(presc.p_issue_date, datetime) else presc.p_issue_date
                self.prescription_tree.insert('', 'end', values=(presc.p_id, presc.cust_id, presc.doctor, issue_date))

    def add_prescription(self):
        try:
            presc_id = self.presc_id.get().strip()
            cust_id = self.presc_cust_id.get().strip()
            doctor = self.presc_doctor.get().strip()
            issue_date = self.presc_issue_date.get_date().strftime('%Y-%m-%d')

            if not presc_id or not cust_id or not doctor:
                messagebox.showerror("Error", "Please enter Prescription ID, Customer ID, and Doctor.")
                return

            query = """
            INSERT INTO Prescription (p_id, cust_id, doctor, p_issue_date)
            VALUES (?, ?, ?, ?)
            """
            params = (
                presc_id,
                cust_id,
                doctor,
                issue_date
            )
            self.execute_db_operation(query, params)
            self.load_prescriptions()
            messagebox.showinfo("Success", "Prescription added successfully!")
            self.clear_prescription_form()
            logging.info(f"Added prescription: {presc_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding prescription: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding prescription: {str(e)}")
            logging.error(f"Error adding prescription: {e}")

    def update_prescription(self):
        try:
            presc_id = self.presc_id.get().strip()
            cust_id = self.presc_cust_id.get().strip()
            doctor = self.presc_doctor.get().strip()
            issue_date = self.presc_issue_date.get_date().strftime('%Y-%m-%d')

            if not presc_id:
                messagebox.showerror("Error", "Please enter Prescription ID.")
                return

            query = """
            UPDATE Prescription
            SET cust_id = ?, doctor = ?, p_issue_date = ?
            WHERE p_id = ?
            """
            params = (
                cust_id,
                doctor,
                issue_date,
                presc_id
            )
            self.execute_db_operation(query, params)
            self.load_prescriptions()
            messagebox.showinfo("Success", "Prescription updated successfully!")
            self.clear_prescription_form()
            logging.info(f"Updated prescription: {presc_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating prescription: {str(e)}")
            logging.error(f"Error updating prescription: {e}")

    def clear_prescription_form(self):
        self.presc_id.delete(0, tk.END)
        self.presc_cust_id.delete(0, tk.END)
        self.presc_doctor.delete(0, tk.END)
        self.presc_issue_date.set_date(datetime.today())

    # -----------------------------
    # Stock Operations
    # -----------------------------
    def create_stock_tab(self):
        stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(stock_frame, text='Stock')

        # Form fields
        form_frame = ttk.LabelFrame(stock_frame, text="Stock Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Medication ID:", "stock_med_id"),
            ("Order ID:", "stock_order_id"),
            ("Quantity:", "stock_qty"),
            ("Production Date:", "production_date"),
            ("Expire Date:", "expire_date"),
            ("Total Price:", "total_price")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            row = idx // 3
            col = (idx % 3) * 2
            ttk.Label(form_frame, text=label_text).grid(row=row, column=col, padx=5, pady=5, sticky='w')
            if var_name in ["production_date", "expire_date"]:
                date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                date_entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, date_entry)
            else:
                entry = ttk.Entry(form_frame)
                entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
                setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(stock_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Stock",
                   command=self.add_stock).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Stock",
                   command=self.update_stock).pack(side='left', padx=5)

        # Treeview for displaying stock
        tree_frame = ttk.Frame(stock_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('Medication ID', 'Order ID', 'Quantity', 'Production Date', 'Expire Date', 'Total Price')
        self.stock_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=120, anchor='center')

        self.stock_tree.pack(fill='both', expand=True)
        self.stock_tree.bind('<<TreeviewSelect>>', self.on_stock_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.stock_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.stock_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_stock()

    def on_stock_select(self, event):
        selected_item = self.stock_tree.focus()
        if selected_item:
            values = self.stock_tree.item(selected_item, 'values')
            self.stock_med_id.delete(0, tk.END)
            self.stock_med_id.insert(0, values[0])
            self.stock_order_id.delete(0, tk.END)
            self.stock_order_id.insert(0, values[1])
            self.stock_qty.delete(0, tk.END)
            self.stock_qty.insert(0, values[2])
            self.production_date.set_date(values[3])
            self.expire_date.set_date(values[4])
            self.total_price.delete(0, tk.END)
            self.total_price.insert(0, values[5])

    def load_stock(self):
        query = """
        SELECT med_id, order_id, s_quantity, production_date, expire_date, total_price
        FROM Stock
        """
        stock = self.execute_db_operation(query)
        self.stock_tree.delete(*self.stock_tree.get_children())
        if stock:
            for item in stock:
                prod_date = item.production_date.strftime('%Y-%m-%d') if isinstance(item.production_date, datetime) else item.production_date
                exp_date = item.expire_date.strftime('%Y-%m-%d') if isinstance(item.expire_date, datetime) else item.expire_date
                self.stock_tree.insert('', 'end', values=(item.med_id, item.order_id, item.s_quantity, prod_date, exp_date, f"{item.total_price:.2f}"))

    def add_stock(self):
        try:
            med_id = self.stock_med_id.get().strip()
            order_id = self.stock_order_id.get().strip()
            quantity = self.stock_qty.get().strip()
            production_date = self.production_date.get_date().strftime('%Y-%m-%d')
            expire_date = self.expire_date.get_date().strftime('%Y-%m-%d')
            total_price = self.total_price.get().strip()

            if not med_id or not order_id or not quantity:
                messagebox.showerror("Error", "Please enter Medication ID, Order ID, and Quantity.")
                return

            if not quantity.isdigit() or not self.is_valid_float(total_price):
                messagebox.showerror("Error", "Quantity must be an integer and Total Price must be a number.")
                return

            query = """
            INSERT INTO Stock (med_id, order_id, s_quantity, production_date, expire_date, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                med_id,
                order_id,
                int(quantity),
                production_date,
                expire_date,
                float(total_price)
            )
            self.execute_db_operation(query, params)
            self.load_stock()
            messagebox.showinfo("Success", "Stock added successfully!")
            self.clear_stock_form()
            logging.info(f"Added stock item: Med ID {med_id}, Order ID {order_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding stock: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding stock: {str(e)}")
            logging.error(f"Error adding stock: {e}")

    def update_stock(self):
        try:
            med_id = self.stock_med_id.get().strip()
            order_id = self.stock_order_id.get().strip()
            quantity = self.stock_qty.get().strip()
            production_date = self.production_date.get_date().strftime('%Y-%m-%d')
            expire_date = self.expire_date.get_date().strftime('%Y-%m-%d')
            total_price = self.total_price.get().strip()

            if not med_id or not order_id:
                messagebox.showerror("Error", "Please enter Medication ID and Order ID.")
                return

            if not quantity.isdigit() or not self.is_valid_float(total_price):
                messagebox.showerror("Error", "Quantity must be an integer and Total Price must be a number.")
                return

            query = """
            UPDATE Stock
            SET s_quantity = ?, production_date = ?, expire_date = ?, total_price = ?
            WHERE med_id = ? AND order_id = ?
            """
            params = (
                int(quantity),
                production_date,
                expire_date,
                float(total_price),
                med_id,
                order_id
            )
            self.execute_db_operation(query, params)
            self.load_stock()
            messagebox.showinfo("Success", "Stock updated successfully!")
            self.clear_stock_form()
            logging.info(f"Updated stock item: Med ID {med_id}, Order ID {order_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating stock: {str(e)}")
            logging.error(f"Error updating stock: {e}")

    def clear_stock_form(self):
        self.stock_med_id.delete(0, tk.END)
        self.stock_order_id.delete(0, tk.END)
        self.stock_qty.delete(0, tk.END)
        self.production_date.set_date(datetime.today())
        self.expire_date.set_date(datetime.today())
        self.total_price.delete(0, tk.END)

    # -----------------------------
    # Suppliers Operations
    # -----------------------------
    def create_suppliers_tab(self):
        suppliers_frame = ttk.Frame(self.notebook)
        self.notebook.add(suppliers_frame, text='Suppliers')

        # Form fields
        form_frame = ttk.LabelFrame(suppliers_frame, text="Supplier Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Supplier ID:", "sup_id"),
            ("Name:", "sup_name"),
            ("Contact Number:", "sup_contact"),
            ("Address ID:", "sup_address"),
            ("Company Name:", "sup_company")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=idx//3, column=(idx%3)*2, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(form_frame)
            entry.grid(row=idx//3, column=(idx%3)*2 + 1, padx=5, pady=5, sticky='w')
            setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(suppliers_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Supplier",
                   command=self.add_supplier).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Supplier",
                   command=self.update_supplier).pack(side='left', padx=5)

        # Treeview for displaying suppliers
        tree_frame = ttk.Frame(suppliers_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Name', 'Contact', 'Address', 'Company Name')
        self.suppliers_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=120, anchor='center')

        self.suppliers_tree.pack(fill='both', expand=True)
        self.suppliers_tree.bind('<<TreeviewSelect>>', self.on_supplier_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.suppliers_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.suppliers_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_suppliers()

    def on_supplier_select(self, event):
        selected_item = self.suppliers_tree.focus()
        if selected_item:
            values = self.suppliers_tree.item(selected_item, 'values')
            self.sup_id.delete(0, tk.END)
            self.sup_id.insert(0, values[0])
            self.sup_name.delete(0, tk.END)
            self.sup_name.insert(0, values[1])
            self.sup_contact.delete(0, tk.END)
            self.sup_contact.insert(0, values[2])
            self.sup_address.delete(0, tk.END)
            self.sup_address.insert(0, values[3])
            self.sup_company.delete(0, tk.END)
            self.sup_company.insert(0, values[4])

    def load_suppliers(self):
        query = """
        SELECT supplier_id, contact_name, address_id, contact_phone, company_name
        FROM Supplier
        """
        suppliers = self.execute_db_operation(query)
        self.suppliers_tree.delete(*self.suppliers_tree.get_children())
        if suppliers:
            for sup in suppliers:
                self.suppliers_tree.insert('', 'end', values=(sup.supplier_id, sup.contact_name, sup.contact_phone, sup.address_id, sup.company_name))

    def add_supplier(self):
        try:
            sup_id = self.sup_id.get().strip()
            sup_name = self.sup_name.get().strip()
            sup_contact = self.sup_contact.get().strip()
            sup_address = self.sup_address.get().strip()
            sup_company = self.sup_company.get().strip()

            if not sup_id or not sup_name:
                messagebox.showerror("Error", "Please enter Supplier ID and Name.")
                return

            query = """
            INSERT INTO Supplier (supplier_id, contact_name, address_id, contact_phone, company_name)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (
                sup_id,
                sup_name,
                sup_address,
                sup_contact,
                sup_company
            )
            self.execute_db_operation(query, params)
            self.load_suppliers()
            messagebox.showinfo("Success", "Supplier added successfully!")
            self.clear_supplier_form()
            logging.info(f"Added supplier: {sup_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding supplier: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding supplier: {str(e)}")
            logging.error(f"Error adding supplier: {e}")

    def update_supplier(self):
        try:
            sup_id = self.sup_id.get().strip()
            sup_name = self.sup_name.get().strip()
            sup_contact = self.sup_contact.get().strip()
            sup_address = self.sup_address.get().strip()
            sup_company = self.sup_company.get().strip()

            if not sup_id:
                messagebox.showerror("Error", "Please enter Supplier ID.")
                return

            query = """
            UPDATE Supplier
            SET contact_name = ?, contact_phone = ?, address_id = ?, company_name = ?
            WHERE supplier_id = ?
            """
            params = (
                sup_name,
                sup_contact,
                sup_address,
                sup_company,
                sup_id
            )
            self.execute_db_operation(query, params)
            self.load_suppliers()
            messagebox.showinfo("Success", "Supplier updated successfully!")
            self.clear_supplier_form()
            logging.info(f"Updated supplier: {sup_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating supplier: {str(e)}")
            logging.error(f"Error updating supplier: {e}")

    def clear_supplier_form(self):
        self.sup_id.delete(0, tk.END)
        self.sup_name.delete(0, tk.END)
        self.sup_contact.delete(0, tk.END)
        self.sup_address.delete(0, tk.END)
        self.sup_company.delete(0, tk.END)

    # -----------------------------
    # Address Dashboard Operations
    # -----------------------------
    def create_address_dashboard_tab(self):
        address_frame = ttk.Frame(self.notebook)
        self.notebook.add(address_frame, text='Address Dashboard')

        # Form fields
        form_frame = ttk.LabelFrame(address_frame, text="Address Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Address ID:", "addr_id"),
            ("Street Name:", "street_name"),
            ("City:", "city"),
            ("Area:", "area"),
            ("Building Name:", "building_name")
        ]

        for idx, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=idx//2, column=(idx%2)*2, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(form_frame)
            entry.grid(row=idx//2, column=(idx%2)*2 + 1, padx=5, pady=5, sticky='w')
            setattr(self, var_name, entry)

        # Buttons
        btn_frame = ttk.Frame(address_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Address",
                   command=self.add_address).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Address",
                   command=self.update_address).pack(side='left', padx=5)

        # Treeview for displaying addresses
        tree_frame = ttk.Frame(address_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Street Name', 'City', 'Area', 'Building Name')
        self.address_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.address_tree.heading(col, text=col)
            self.address_tree.column(col, width=120, anchor='center')

        self.address_tree.pack(fill='both', expand=True)
        self.address_tree.bind('<<TreeviewSelect>>', self.on_address_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.address_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.address_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_addresses()

    def on_address_select(self, event):
        selected_item = self.address_tree.focus()
        if selected_item:
            values = self.address_tree.item(selected_item, 'values')
            self.addr_id.delete(0, tk.END)
            self.addr_id.insert(0, values[0])
            self.street_name.delete(0, tk.END)
            self.street_name.insert(0, values[1])
            self.city.delete(0, tk.END)
            self.city.insert(0, values[2])
            self.area.delete(0, tk.END)
            self.area.insert(0, values[3])
            self.building_name.delete(0, tk.END)
            self.building_name.insert(0, values[4])

    def load_addresses(self):
        query = """
        SELECT address_id, Street_name, City, Area, Building_name
        FROM Address
        """
        addresses = self.execute_db_operation(query)
        self.address_tree.delete(*self.address_tree.get_children())
        if addresses:
            for addr in addresses:
                self.address_tree.insert('', 'end', values=(addr.address_id, addr.Street_name, addr.City, addr.Area, addr.Building_name))

    def add_address(self):
        try:
            addr_id = self.addr_id.get().strip()
            street_name = self.street_name.get().strip()
            city = self.city.get().strip()
            area = self.area.get().strip()
            building_name = self.building_name.get().strip()

            if not addr_id or not street_name or not city:
                messagebox.showerror("Error", "Please enter Address ID, Street Name, and City.")
                return

            query = """
            INSERT INTO Address (address_id, Street_name, City, Area, Building_name)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (
                addr_id,
                street_name,
                city,
                area,
                building_name
            )
            self.execute_db_operation(query, params)
            self.load_addresses()
            messagebox.showinfo("Success", "Address added successfully!")
            self.clear_address_form()
            logging.info(f"Added address: {addr_id}")
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Error", f"Database Integrity Error: {str(e)}")
            logging.error(f"IntegrityError while adding address: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding address: {str(e)}")
            logging.error(f"Error adding address: {e}")

    def update_address(self):
        try:
            addr_id = self.addr_id.get().strip()
            street_name = self.street_name.get().strip()
            city = self.city.get().strip()
            area = self.area.get().strip()
            building_name = self.building_name.get().strip()

            if not addr_id:
                messagebox.showerror("Error", "Please enter Address ID.")
                return

            query = """
            UPDATE Address
            SET Street_name = ?, City = ?, Area = ?, Building_name = ?
            WHERE address_id = ?
            """
            params = (
                street_name,
                city,
                area,
                building_name,
                addr_id
            )
            self.execute_db_operation(query, params)
            self.load_addresses()
            messagebox.showinfo("Success", "Address updated successfully!")
            self.clear_address_form()
            logging.info(f"Updated address: {addr_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating address: {str(e)}")
            logging.error(f"Error updating address: {e}")

    def clear_address_form(self):
        self.addr_id.delete(0, tk.END)
        self.street_name.delete(0, tk.END)
        self.city.delete(0, tk.END)
        self.area.delete(0, tk.END)
        self.building_name.delete(0, tk.END)

    # -----------------------------
    # Monthly Orders Statement Operations
    # -----------------------------
    def create_monthly_orders_tab(self):
        orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(orders_frame, text='Monthly Orders')

        # Date selection
        date_frame = ttk.LabelFrame(orders_frame, text="Select Month", padding=10)
        date_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(date_frame, text="Month:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.order_month = ttk.Combobox(date_frame, values=[
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'], state='readonly')
        self.order_month.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(date_frame, text="Year:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        current_year = datetime.now().year
        self.order_year = ttk.Entry(date_frame)
        self.order_year.insert(0, str(current_year))
        self.order_year.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Button(date_frame, text="Generate Report",
                   command=self.generate_order_report).grid(row=0, column=4, padx=5, pady=5, sticky='w')

        # Treeview for displaying orders
        tree_frame = ttk.Frame(orders_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('Statement ID', 'Supplier ID', 'Year', 'Month',
                   'Status', 'Issue Date', 'Total')
        self.orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120, anchor='center')

        self.orders_tree.pack(fill='both', expand=True)
        self.orders_tree.bind('<<TreeviewSelect>>', self.on_order_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.orders_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_monthly_orders()

    def generate_order_report(self):
        month = self.order_month.get()
        year = self.order_year.get().strip()
        if not month or not year:
            messagebox.showerror("Error", "Please select both month and year.")
            return

        try:
            month_number = datetime.strptime(month, '%B').month
            year = int(year)
        except ValueError:
            messagebox.showerror("Error", "Invalid month or year.")
            return

        query = """
        SELECT O_statement_id, supplier_id, O_year, O_month, O_status, O_issue_date, O_statement_total
        FROM Order_monthly_statement
        WHERE O_month = ? AND O_year = ?
        """
        orders = self.execute_db_operation(query, (month_number, year))
        self.orders_tree.delete(*self.orders_tree.get_children())
        if orders:
            for order in orders:
                issue_date = order.O_issue_date.strftime('%Y-%m-%d') if isinstance(order.O_issue_date, datetime) else order.O_issue_date
                self.orders_tree.insert('', 'end', values=(order.O_statement_id, order.supplier_id, order.O_year, order.O_month, order.O_status, issue_date, f"{order.O_statement_total:.2f}"))
        else:
            messagebox.showinfo("Info", "No orders found for the selected month and year.")

    def load_monthly_orders(self):
        query = """
        SELECT O_statement_id, supplier_id, O_year, O_month, O_status, O_issue_date, O_statement_total
        FROM Order_monthly_statement
        """
        orders = self.execute_db_operation(query)
        self.orders_tree.delete(*self.orders_tree.get_children())
        if orders:
            for order in orders:
                issue_date = order.O_issue_date.strftime('%Y-%m-%d') if isinstance(order.O_issue_date, datetime) else order.O_issue_date
                self.orders_tree.insert('', 'end', values=(order.O_statement_id, order.supplier_id, order.O_year, order.O_month, order.O_status, issue_date, f"{order.O_statement_total:.2f}"))

    def on_order_select(self, event):
        selected_item = self.orders_tree.focus()
        if selected_item:
            values = self.orders_tree.item(selected_item, 'values')
            # Implement additional functionalities if needed

    # -----------------------------
    # Monthly Sales Statement Operations
    # -----------------------------
    def create_monthly_sales_tab(self):
        sales_statement_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_statement_frame, text='Monthly Sales')

        # Date selection
        date_frame = ttk.LabelFrame(sales_statement_frame, text="Select Month", padding=10)
        date_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(date_frame, text="Month:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sales_month = ttk.Combobox(date_frame, values=[
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'], state='readonly')
        self.sales_month.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(date_frame, text="Year:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        current_year = datetime.now().year
        self.sales_year = ttk.Entry(date_frame)
        self.sales_year.insert(0, str(current_year))
        self.sales_year.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Button(date_frame, text="Generate Report",
                   command=self.generate_sales_report).grid(row=0, column=4, padx=5, pady=5, sticky='w')

        # Treeview for displaying sales
        tree_frame = ttk.Frame(sales_statement_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('Sale ID', 'Year', 'Month', 'Issue Date', 'Total')
        self.sales_statement_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.sales_statement_tree.heading(col, text=col)
            self.sales_statement_tree.column(col, width=120, anchor='center')

        self.sales_statement_tree.pack(fill='both', expand=True)
        self.sales_statement_tree.bind('<<TreeviewSelect>>', self.on_sales_statement_select)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.sales_statement_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.sales_statement_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_monthly_sales()

    def generate_sales_report(self):
        month = self.sales_month.get()
        year = self.sales_year.get().strip()
        if not month or not year:
            messagebox.showerror("Error", "Please select both month and year.")
            return

        try:
            month_number = datetime.strptime(month, '%B').month
            year = int(year)
        except ValueError:
            messagebox.showerror("Error", "Invalid month or year.")
            return

        query = """
        SELECT s_id, year, month, issue_date, S_Statement_total
        FROM sales_monthly_statement
        WHERE month = ? AND year = ?
        """
        sales = self.execute_db_operation(query, (month_number, year))
        self.sales_statement_tree.delete(*self.sales_statement_tree.get_children())
        if sales:
            for sale in sales:
                issue_date = sale.issue_date.strftime('%Y-%m-%d') if isinstance(sale.issue_date, datetime) else sale.issue_date
                self.sales_statement_tree.insert('', 'end', values=(sale.s_id, sale.year, sale.month, issue_date, f"{sale.S_Statement_total:.2f}"))
        else:
            messagebox.showinfo("Info", "No sales found for the selected month and year.")

    def load_monthly_sales(self):
        query = """
        SELECT s_id, year, month, issue_date, S_Statement_total
        FROM sales_monthly_statement
        """
        sales = self.execute_db_operation(query)
        self.sales_statement_tree.delete(*self.sales_statement_tree.get_children())
        if sales:
            for sale in sales:
                issue_date = sale.issue_date.strftime('%Y-%m-%d') if isinstance(sale.issue_date, datetime) else sale.issue_date
                self.sales_statement_tree.insert('', 'end', values=(sale.s_id, sale.year, sale.month, issue_date, f"{sale.S_Statement_total:.2f}"))

    def on_sales_statement_select(self, event):
        selected_item = self.sales_statement_tree.focus()
        if selected_item:
            values = self.sales_statement_tree.item(selected_item, 'values')
            # Implement additional functionalities if needed

    # -----------------------------
    # Database Operations
    # -----------------------------
    def execute_db_operation(self, query, params=None):
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = None
                cursor.close()
                return result
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            logging.error(f"Database operation error: {e}")
            return None

    # -----------------------------
    # Application Entry Point
    # -----------------------------
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Pharmacy Management System')
    parser.add_argument('--server', help='SQL Server instance name')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--log-file', help='Log file path')
    args = parser.parse_args()

    # Create config
    config = PharmacyConfig()

    # Override config with command line arguments
    if args.server:
        config.server = args.server
    if args.database:
        config.database = args.database
    if args.log_file:
        config.log_file = args.log_file

    try:
        # Initialize GUI
        root = tk.Tk()
        app = PharmacyManagementSystem(root, config)

        # Start application
        logging.info("Application started.")
        root.mainloop()

    except Exception as e:
        logging.error(f"Application error: {e}")
        messagebox.showerror("Error", f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
