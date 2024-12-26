import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import argparse
import logging
from datetime import datetime
from pathlib import Path
from tkcalendar import DateEntry


class PharmacyConfig:
    def __init__(self):
        self.server = 'LAPTOP-VIO2PNI9'
        self.database = 'project2'
        self.trusted_connection = 'yes'
        self.log_file = 'logs/pharmacy.log'


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

        ttk.Label(form_frame, text="Customer ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.cust_id = ttk.Entry(form_frame)
        self.cust_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.cust_name = ttk.Entry(form_frame)
        self.cust_name.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Phone:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.cust_phone = ttk.Entry(form_frame)
        self.cust_phone.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Date of Birth:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.date_birth = DateEntry(form_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.date_birth.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Gender:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.gender = ttk.Combobox(form_frame, values=['M', 'F'], state='readonly')
        self.gender.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Insurance:").grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.insurance = ttk.Combobox(form_frame, values=['YES', 'NO'], state='readonly')
        self.insurance.grid(row=1, column=5, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(customers_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Customer",
                   command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Customer",
                   command=self.update_customer).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Customer",
                   command=self.delete_customer).pack(side='left', padx=5)

        # Treeview for displaying customers
        tree_frame = ttk.Frame(customers_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.customer_tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Phone', 'DOB',
                                                                 'Gender', 'Insurance'),
                                         show='headings')
        self.customer_tree.heading('ID', text='ID')
        self.customer_tree.heading('Name', text='Name')
        self.customer_tree.heading('Phone', text='Phone')
        self.customer_tree.heading('DOB', text='Date of Birth')
        self.customer_tree.heading('Gender', text='Gender')
        self.customer_tree.heading('Insurance', text='Insurance')

        for col in ('ID', 'Name', 'Phone', 'DOB', 'Gender', 'Insurance'):
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
                self.customer_tree.insert('', 'end', values=customer)

    def add_customer(self):
        try:
            cust_id = self.cust_id.get()
            cust_name = self.cust_name.get()
            cust_phone = self.cust_phone.get()
            date_birth = self.date_birth.get_date()
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
            cust_id = self.cust_id.get()
            cust_name = self.cust_name.get()
            cust_phone = self.cust_phone.get()
            date_birth = self.date_birth.get_date()
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

    def delete_customer(self):
        cust_id = self.cust_id.get()
        if not cust_id:
            messagebox.showerror("Error", "Please enter Customer ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
            try:
                query = "DELETE FROM Customer WHERE cust_id = ?"
                self.execute_db_operation(query, (cust_id,))
                self.load_customers()
                messagebox.showinfo("Success", "Customer deleted successfully!")
                self.clear_customer_form()
                logging.info(f"Deleted customer: {cust_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting customer: {str(e)}")
                logging.error(f"Error deleting customer: {e}")

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

        ttk.Label(form_frame, text="Employee ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.emp_id = ttk.Entry(form_frame)
        self.emp_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Title:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.emp_title = ttk.Entry(form_frame)
        self.emp_title.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Name:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.emp_name = ttk.Entry(form_frame)
        self.emp_name.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.emp_phone = ttk.Entry(form_frame)
        self.emp_phone.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Date of Birth:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.emp_dob = DateEntry(form_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2)
        self.emp_dob.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Gender:").grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.emp_gender = ttk.Combobox(form_frame, values=['M', 'F'], state='readonly')
        self.emp_gender.grid(row=1, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Hire Date:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.hire_date = DateEntry(form_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.hire_date.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Salary:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.salary = ttk.Entry(form_frame)
        self.salary.grid(row=2, column=3, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(employees_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Employee",
                   command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Employee",
                   command=self.update_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Employee",
                   command=self.delete_employee).pack(side='left', padx=5)

        # Treeview for displaying employees
        tree_frame = ttk.Frame(employees_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.employee_tree = ttk.Treeview(tree_frame,
                                          columns=('ID', 'Title', 'Name', 'Phone', 'DOB',
                                                   'Gender', 'Hire Date', 'Salary'),
                                          show='headings')
        self.employee_tree.heading('ID', text='ID')
        self.employee_tree.heading('Title', text='Title')
        self.employee_tree.heading('Name', text='Name')
        self.employee_tree.heading('Phone', text='Phone')
        self.employee_tree.heading('DOB', text='Date of Birth')
        self.employee_tree.heading('Gender', text='Gender')
        self.employee_tree.heading('Hire Date', text='Hire Date')
        self.employee_tree.heading('Salary', text='Salary')

        for col in ('ID', 'Title', 'Name', 'Phone', 'DOB', 'Gender', 'Hire Date', 'Salary'):
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
                self.employee_tree.insert('', 'end', values=employee)

    def add_employee(self):
        try:
            emp_id = self.emp_id.get()
            emp_title = self.emp_title.get()
            emp_name = self.emp_name.get()
            emp_phone = self.emp_phone.get()
            emp_dob = self.emp_dob.get_date()
            emp_gender = self.emp_gender.get()
            hire_date = self.hire_date.get_date()
            salary = self.salary.get()

            if not emp_id or not emp_name:
                messagebox.showerror("Error", "Please enter Employee ID and Name.")
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
                salary
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
            emp_id = self.emp_id.get()
            emp_title = self.emp_title.get()
            emp_name = self.emp_name.get()
            emp_phone = self.emp_phone.get()
            emp_dob = self.emp_dob.get_date()
            emp_gender = self.emp_gender.get()
            hire_date = self.hire_date.get_date()
            salary = self.salary.get()

            if not emp_id:
                messagebox.showerror("Error", "Please enter Employee ID.")
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
                salary,
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

    def delete_employee(self):
        emp_id = self.emp_id.get()
        if not emp_id:
            messagebox.showerror("Error", "Please enter Employee ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this employee?"):
            try:
                query = "DELETE FROM Employee WHERE emp_id = ?"
                self.execute_db_operation(query, (emp_id,))
                self.load_employees()
                messagebox.showinfo("Success", "Employee deleted successfully!")
                self.clear_employee_form()
                logging.info(f"Deleted employee: {emp_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting employee: {str(e)}")
                logging.error(f"Error deleting employee: {e}")

    def clear_employee_form(self):
        self.emp_id.delete(0, tk.END)
        self.emp_title.delete(0, tk.END)
        self.emp_name.delete(0, tk.END)
        self.emp_phone.delete(0, tk.END)
        self.emp_dob.set_date(datetime.today())
        self.emp_gender.set('')
        self.hire_date.set_date(datetime.today())
        self.salary.delete(0, tk.END)

    # -----------------------------
    # Medications Operations
    # -----------------------------
    def create_medications_tab(self):
        medications_frame = ttk.Frame(self.notebook)
        self.notebook.add(medications_frame, text='Medications')

        # Form fields
        form_frame = ttk.LabelFrame(medications_frame, text="Medication Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Medication ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.med_id = ttk.Entry(form_frame)
        self.med_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.med_name = ttk.Entry(form_frame)
        self.med_name.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Manufacturer:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.manufacturer = ttk.Entry(form_frame)
        self.manufacturer.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.med_price = ttk.Entry(form_frame)
        self.med_price.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.med_quantity = ttk.Entry(form_frame)
        self.med_quantity.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(medications_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Medication",
                   command=self.add_medication).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Medication",
                   command=self.update_medication).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Medication",
                   command=self.delete_medication).pack(side='left', padx=5)

        # Treeview
        tree_frame = ttk.Frame(medications_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.medication_tree = ttk.Treeview(tree_frame,
                                            columns=('ID', 'Name', 'Manufacturer',
                                                     'Price', 'Quantity'),
                                            show='headings')
        self.medication_tree.heading('ID', text='ID')
        self.medication_tree.heading('Name', text='Name')
        self.medication_tree.heading('Manufacturer', text='Manufacturer')
        self.medication_tree.heading('Price', text='Price')
        self.medication_tree.heading('Quantity', text='Quantity')

        for col in ('ID', 'Name', 'Manufacturer', 'Price', 'Quantity'):
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
                self.medication_tree.insert('', 'end', values=med)

    def add_medication(self):
        try:
            med_id = self.med_id.get()
            med_name = self.med_name.get()
            manufacturer = self.manufacturer.get()
            price = self.med_price.get()
            quantity = self.med_quantity.get()

            if not med_id or not med_name:
                messagebox.showerror("Error", "Please enter Medication ID and Name.")
                return

            query = """
            INSERT INTO Medication (med_id, med_name, manufacture, price, med_quantity)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (
                med_id,
                med_name,
                manufacturer,
                price,
                quantity
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
            med_id = self.med_id.get()
            med_name = self.med_name.get()
            manufacturer = self.manufacturer.get()
            price = self.med_price.get()
            quantity = self.med_quantity.get()

            if not med_id:
                messagebox.showerror("Error", "Please enter Medication ID.")
                return

            query = """
            UPDATE Medication
            SET med_name = ?, manufacture = ?, price = ?, med_quantity = ?
            WHERE med_id = ?
            """
            params = (
                med_name,
                manufacturer,
                price,
                quantity,
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

    def delete_medication(self):
        med_id = self.med_id.get()
        if not med_id:
            messagebox.showerror("Error", "Please enter Medication ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this medication?"):
            try:
                query = "DELETE FROM Medication WHERE med_id = ?"
                self.execute_db_operation(query, (med_id,))
                self.load_medications()
                messagebox.showinfo("Success", "Medication deleted successfully!")
                self.clear_medication_form()
                logging.info(f"Deleted medication: {med_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting medication: {str(e)}")
                logging.error(f"Error deleting medication: {e}")

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

        ttk.Label(form_frame, text="Sale ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sale_id = ttk.Entry(form_frame)
        self.sale_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Customer ID:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.sale_cust_id = ttk.Entry(form_frame)
        self.sale_cust_id.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Employee ID:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.sale_emp_id = ttk.Entry(form_frame)
        self.sale_emp_id.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Sale Type:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.sale_type = ttk.Combobox(form_frame, values=['pickup', 'delivery'], state='readonly')
        self.sale_type.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Payment Method:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.payment_method = ttk.Combobox(form_frame, values=['CASH', 'VISA', 'INSURANCE'], state='readonly')
        self.payment_method.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Sale Date:").grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.sale_date = DateEntry(form_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.sale_date.grid(row=1, column=5, padx=5, pady=5, sticky='w')

        # Sale Details Frame
        details_frame = ttk.LabelFrame(sales_frame, text="Sale Items", padding=10)
        details_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(details_frame, text="Medication ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sale_med_id = ttk.Entry(details_frame)
        self.sale_med_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(details_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.sale_quantity = ttk.Entry(details_frame)
        self.sale_quantity.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Button(details_frame, text="Add Item",
                   command=self.add_sale_item).grid(row=0, column=4, padx=5, pady=5, sticky='w')

        # Sale Items Treeview
        self.sales_details_tree = ttk.Treeview(details_frame,
                                               columns=('Medication ID', 'Name', 'Unit Price', 'Quantity', 'Total'),
                                               show='headings')
        self.sales_details_tree.heading('Medication ID', text='Medication ID')
        self.sales_details_tree.heading('Name', text='Name')
        self.sales_details_tree.heading('Unit Price', text='Unit Price')
        self.sales_details_tree.heading('Quantity', text='Quantity')
        self.sales_details_tree.heading('Total', text='Total')

        for col in ('Medication ID', 'Name', 'Unit Price', 'Quantity', 'Total'):
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

        # Sales Treeview
        tree_frame = ttk.Frame(sales_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.sales_tree = ttk.Treeview(tree_frame,
                                       columns=('ID', 'Customer', 'Employee', 'Type',
                                                'Payment', 'Date', 'Total'),
                                       show='headings')
        self.sales_tree.heading('ID', text='Sale ID')
        self.sales_tree.heading('Customer', text='Customer ID')
        self.sales_tree.heading('Employee', text='Employee ID')
        self.sales_tree.heading('Type', text='Sale Type')
        self.sales_tree.heading('Payment', text='Payment Method')
        self.sales_tree.heading('Date', text='Date')
        self.sales_tree.heading('Total', text='Total')

        for col in ('ID', 'Customer', 'Employee', 'Type', 'Payment', 'Date', 'Total'):
            self.sales_tree.column(col, width=100, anchor='center')

        self.sales_tree.pack(fill='both', expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.sales_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.sales_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_sales()
        self.current_sale_total = 0.0

    def add_sale_item(self):
        med_id = self.sale_med_id.get()
        quantity = self.sale_quantity.get()
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
        self.sales_details_tree.insert('', 'end', values=(med_id, med_name, unit_price, quantity, total_price))
        self.current_sale_total += total_price
        self.sale_total_label.config(text=f"Total: ${self.current_sale_total:.2f}")
        self.sale_med_id.delete(0, tk.END)
        self.sale_quantity.delete(0, tk.END)

    def complete_sale(self):
        sale_id = self.sale_id.get()
        cust_id = self.sale_cust_id.get()
        emp_id = self.sale_emp_id.get()
        sale_type = self.sale_type.get()
        payment_method = self.payment_method.get()
        sale_date = self.sale_date.get_date()

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
                    unit_price,
                    quantity,
                    total
                )
                self.execute_db_operation(query_details, params_details)

                # Update Medication quantity
                query_update = """
                UPDATE Medication
                SET med_quantity = med_quantity - ?
                WHERE med_id = ?
                """
                self.execute_db_operation(query_update, (quantity, med_id))

            # Update Stock related to Sales Details
            for child in self.sales_details_tree.get_children():
                med_id, _, _, quantity, _ = self.sales_details_tree.item(child, 'values')
                # Assume there's a relation between Medication and Stock
                query_stock = """
                SELECT order_id, s_quantity
                FROM Stock
                WHERE med_id = ?
                ORDER BY production_date DESC
                """
                stock_items = self.execute_db_operation(query_stock, (med_id,))
                remaining = quantity
                for stock in stock_items:
                    order_id, available_qty = stock
                    if available_qty >= remaining:
                        query_update_stock = """
                        UPDATE Stock
                        SET s_quantity = s_quantity - ?
                        WHERE med_id = ? AND order_id = ?
                        """
                        self.execute_db_operation(query_update_stock, (remaining, med_id, order_id))
                        break
                    else:
                        query_update_stock = """
                        UPDATE Stock
                        SET s_quantity = 0
                        WHERE med_id = ? AND order_id = ?
                        """
                        self.execute_db_operation(query_update_stock, (med_id, order_id))
                        remaining -= available_qty

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
                self.sales_tree.insert('', 'end', values=sale)

    # -----------------------------
    # Prescriptions Operations
    # -----------------------------
    def create_prescriptions_tab(self):
        prescriptions_frame = ttk.Frame(self.notebook)
        self.notebook.add(prescriptions_frame, text='Prescriptions')

        # Form fields
        form_frame = ttk.LabelFrame(prescriptions_frame, text="Prescription Details", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Prescription ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.presc_id = ttk.Entry(form_frame)
        self.presc_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Customer ID:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.presc_cust_id = ttk.Entry(form_frame)
        self.presc_cust_id.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Doctor:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.presc_doctor = ttk.Entry(form_frame)
        self.presc_doctor.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Issue Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.presc_issue_date = DateEntry(form_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2)
        self.presc_issue_date.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(prescriptions_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Prescription",
                   command=self.add_prescription).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Prescription",
                   command=self.update_prescription).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Prescription",
                   command=self.delete_prescription).pack(side='left', padx=5)

        # Treeview for displaying prescriptions
        tree_frame = ttk.Frame(prescriptions_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.prescription_tree = ttk.Treeview(tree_frame,
                                              columns=('ID', 'Customer', 'Doctor',
                                                       'Issue Date'),
                                              show='headings')
        self.prescription_tree.heading('ID', text='Prescription ID')
        self.prescription_tree.heading('Customer', text='Customer ID')
        self.prescription_tree.heading('Doctor', text='Doctor')
        self.prescription_tree.heading('Issue Date', text='Issue Date')

        for col in ('ID', 'Customer', 'Doctor', 'Issue Date'):
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
                self.prescription_tree.insert('', 'end', values=presc)

    def add_prescription(self):
        try:
            presc_id = self.presc_id.get()
            cust_id = self.presc_cust_id.get()
            doctor = self.presc_doctor.get()
            issue_date = self.presc_issue_date.get_date()

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
            presc_id = self.presc_id.get()
            cust_id = self.presc_cust_id.get()
            doctor = self.presc_doctor.get()
            issue_date = self.presc_issue_date.get_date()

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

    def delete_prescription(self):
        presc_id = self.presc_id.get()
        if not presc_id:
            messagebox.showerror("Error", "Please enter Prescription ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this prescription?"):
            try:
                query = "DELETE FROM Prescription WHERE p_id = ?"
                self.execute_db_operation(query, (presc_id,))
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription deleted successfully!")
                self.clear_prescription_form()
                logging.info(f"Deleted prescription: {presc_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting prescription: {str(e)}")
                logging.error(f"Error deleting prescription: {e}")

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

        ttk.Label(form_frame, text="Medication ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.stock_med_id = ttk.Entry(form_frame)
        self.stock_med_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Order ID:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.stock_order_id = ttk.Entry(form_frame)
        self.stock_order_id.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Quantity:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.stock_qty = ttk.Entry(form_frame)
        self.stock_qty.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Production Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.production_date = DateEntry(form_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2)
        self.production_date.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Expire Date:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.expire_date = DateEntry(form_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2)
        self.expire_date.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Total Price:").grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.total_price = ttk.Entry(form_frame)
        self.total_price.grid(row=1, column=5, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(stock_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Stock",
                   command=self.add_stock).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Stock",
                   command=self.update_stock).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Stock",
                   command=self.delete_stock).pack(side='left', padx=5)

        # Treeview for displaying stock
        tree_frame = ttk.Frame(stock_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.stock_tree = ttk.Treeview(tree_frame,
                                       columns=('Medication ID', 'Order ID', 'Quantity',
                                                'Production Date', 'Expire Date', 'Total Price'),
                                       show='headings')
        self.stock_tree.heading('Medication ID', text='Medication ID')
        self.stock_tree.heading('Order ID', text='Order ID')
        self.stock_tree.heading('Quantity', text='Quantity')
        self.stock_tree.heading('Production Date', text='Production Date')
        self.stock_tree.heading('Expire Date', text='Expire Date')
        self.stock_tree.heading('Total Price', text='Total Price')

        for col in ('Medication ID', 'Order ID', 'Quantity', 'Production Date', 'Expire Date', 'Total Price'):
            self.stock_tree.column(col, width=100, anchor='center')

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
                self.stock_tree.insert('', 'end', values=item)

    def add_stock(self):
        try:
            med_id = self.stock_med_id.get()
            order_id = self.stock_order_id.get()
            quantity = self.stock_qty.get()
            production_date = self.production_date.get_date()
            expire_date = self.expire_date.get_date()
            total_price = self.total_price.get()

            if not med_id or not order_id or not quantity:
                messagebox.showerror("Error", "Please enter Medication ID, Order ID, and Quantity.")
                return

            query = """
            INSERT INTO Stock (med_id, order_id, s_quantity, production_date, expire_date, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                med_id,
                order_id,
                quantity,
                production_date,
                expire_date,
                total_price
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
            med_id = self.stock_med_id.get()
            order_id = self.stock_order_id.get()
            quantity = self.stock_qty.get()
            production_date = self.production_date.get_date()
            expire_date = self.expire_date.get_date()
            total_price = self.total_price.get()

            if not med_id or not order_id:
                messagebox.showerror("Error", "Please enter Medication ID and Order ID.")
                return

            query = """
            UPDATE Stock
            SET s_quantity = ?, production_date = ?, expire_date = ?, total_price = ?
            WHERE med_id = ? AND order_id = ?
            """
            params = (
                quantity,
                production_date,
                expire_date,
                total_price,
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

    def delete_stock(self):
        med_id = self.stock_med_id.get()
        order_id = self.stock_order_id.get()
        if not med_id or not order_id:
            messagebox.showerror("Error", "Please enter Medication ID and Order ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this stock item?"):
            try:
                query = "DELETE FROM Stock WHERE med_id = ? AND order_id = ?"
                self.execute_db_operation(query, (med_id, order_id))
                self.load_stock()
                messagebox.showinfo("Success", "Stock deleted successfully!")
                self.clear_stock_form()
                logging.info(f"Deleted stock item: Med ID {med_id}, Order ID {order_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting stock: {str(e)}")
                logging.error(f"Error deleting stock: {e}")

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

        ttk.Label(form_frame, text="Supplier ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sup_id = ttk.Entry(form_frame)
        self.sup_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.sup_name = ttk.Entry(form_frame)
        self.sup_name.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Contact Number:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.sup_contact = ttk.Entry(form_frame)
        self.sup_contact.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Address ID:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.sup_address = ttk.Entry(form_frame)
        self.sup_address.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Company Name:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.sup_company = ttk.Entry(form_frame)
        self.sup_company.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(suppliers_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Supplier",
                   command=self.add_supplier).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Supplier",
                   command=self.update_supplier).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Supplier",
                   command=self.delete_supplier).pack(side='left', padx=5)

        # Treeview for displaying suppliers
        tree_frame = ttk.Frame(suppliers_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.suppliers_tree = ttk.Treeview(tree_frame,
                                           columns=('ID', 'Name', 'Contact', 'Address', 'Company Name'),
                                           show='headings')
        self.suppliers_tree.heading('ID', text='Supplier ID')
        self.suppliers_tree.heading('Name', text='Name')
        self.suppliers_tree.heading('Contact', text='Contact Number')
        self.suppliers_tree.heading('Address', text='Address ID')
        self.suppliers_tree.heading('Company Name', text='Company Name')

        for col in ('ID', 'Name', 'Contact', 'Address', 'Company Name'):
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
                self.suppliers_tree.insert('', 'end', values=sup)

    def add_supplier(self):
        try:
            sup_id = self.sup_id.get()
            sup_name = self.sup_name.get()
            sup_contact = self.sup_contact.get()
            sup_address = self.sup_address.get()
            sup_company = self.sup_company.get()

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
            sup_id = self.sup_id.get()
            sup_name = self.sup_name.get()
            sup_contact = self.sup_contact.get()
            sup_address = self.sup_address.get()
            sup_company = self.sup_company.get()

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

    def delete_supplier(self):
        sup_id = self.sup_id.get()
        if not sup_id:
            messagebox.showerror("Error", "Please enter Supplier ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this supplier?"):
            try:
                query = "DELETE FROM Supplier WHERE supplier_id = ?"
                self.execute_db_operation(query, (sup_id,))
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier deleted successfully!")
                self.clear_supplier_form()
                logging.info(f"Deleted supplier: {sup_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting supplier: {str(e)}")
                logging.error(f"Error deleting supplier: {e}")

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

        ttk.Label(form_frame, text="Address ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.addr_id = ttk.Entry(form_frame)
        self.addr_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Street Name:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.street_name = ttk.Entry(form_frame)
        self.street_name.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="City:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.city = ttk.Entry(form_frame)
        self.city.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Area:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.area = ttk.Entry(form_frame)
        self.area.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Building Name:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.building_name = ttk.Entry(form_frame)
        self.building_name.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(address_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Address",
                   command=self.add_address).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Address",
                   command=self.update_address).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Address",
                   command=self.delete_address).pack(side='left', padx=5)

        # Treeview for displaying addresses
        tree_frame = ttk.Frame(address_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.address_tree = ttk.Treeview(tree_frame,
                                         columns=('ID', 'Street Name', 'City', 'Area', 'Building Name'),
                                         show='headings')
        self.address_tree.heading('ID', text='Address ID')
        self.address_tree.heading('Street Name', text='Street Name')
        self.address_tree.heading('City', text='City')
        self.address_tree.heading('Area', text='Area')
        self.address_tree.heading('Building Name', text='Building Name')

        for col in ('ID', 'Street Name', 'City', 'Area', 'Building Name'):
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
        SELECT TOP (1000) address_id, Street_name, City, Area, Building_name
        FROM [project2].[dbo].[Address]
        """
        addresses = self.execute_db_operation(query)
        self.address_tree.delete(*self.address_tree.get_children())
        if addresses:
            for addr in addresses:
                self.address_tree.insert('', 'end', values=addr)

    def add_address(self):
        try:
            addr_id = self.addr_id.get()
            street_name = self.street_name.get()
            city = self.city.get()
            area = self.area.get()
            building_name = self.building_name.get()

            if not addr_id or not street_name or not city:
                messagebox.showerror("Error", "Please enter Address ID, Street Name, and City.")
                return

            query = """
            INSERT INTO [project2].[dbo].[Address] (address_id, Street_name, City, Area, Building_name)
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
            addr_id = self.addr_id.get()
            street_name = self.street_name.get()
            city = self.city.get()
            area = self.area.get()
            building_name = self.building_name.get()

            if not addr_id:
                messagebox.showerror("Error", "Please enter Address ID.")
                return

            query = """
            UPDATE [project2].[dbo].[Address]
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

    def delete_address(self):
        addr_id = self.addr_id.get()
        if not addr_id:
            messagebox.showerror("Error", "Please enter Address ID to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this address?"):
            try:
                query = "DELETE FROM [project2].[dbo].[Address] WHERE address_id = ?"
                self.execute_db_operation(query, (addr_id,))
                self.load_addresses()
                messagebox.showinfo("Success", "Address deleted successfully!")
                self.clear_address_form()
                logging.info(f"Deleted address: {addr_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting address: {str(e)}")
                logging.error(f"Error deleting address: {e}")

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

        self.orders_tree = ttk.Treeview(tree_frame,
                                        columns=('O_statement_id', 'supplier_id', 'O_year', 'O_month',
                                                 'O_status', 'O_issue_date', 'O_statement_total'),
                                        show='headings')
        self.orders_tree.heading('O_statement_id', text='Statement ID')
        self.orders_tree.heading('supplier_id', text='Supplier ID')
        self.orders_tree.heading('O_year', text='Year')
        self.orders_tree.heading('O_month', text='Month')
        self.orders_tree.heading('O_status', text='Status')
        self.orders_tree.heading('O_issue_date', text='Issue Date')
        self.orders_tree.heading('O_statement_total', text='Total')

        for col in ('O_statement_id', 'supplier_id', 'O_year', 'O_month', 'O_status', 'O_issue_date', 'O_statement_total'):
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
        year = self.order_year.get()
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
        SELECT TOP (1000) O_statement_id, supplier_id, O_year, O_month, O_status, O_issue_date, O_statement_total
        FROM [project2].[dbo].[Order_monthly_statement]
        WHERE O_month = ? AND O_year = ?
        """
        orders = self.execute_db_operation(query, (month_number, year))
        self.orders_tree.delete(*self.orders_tree.get_children())
        if orders:
            for order in orders:
                self.orders_tree.insert('', 'end', values=order)
        else:
            messagebox.showinfo("Info", "No orders found for the selected month and year.")

    def load_monthly_orders(self):
        query = """
        SELECT TOP (1000) O_statement_id, supplier_id, O_year, O_month, O_status, O_issue_date, O_statement_total
        FROM [project2].[dbo].[Order_monthly_statement]
        """
        orders = self.execute_db_operation(query)
        self.orders_tree.delete(*self.orders_tree.get_children())
        if orders:
            for order in orders:
                self.orders_tree.insert('', 'end', values=order)

    def on_order_select(self, event):
        selected_item = self.orders_tree.focus()
        if selected_item:
            values = self.orders_tree.item(selected_item, 'values')
            self.addr_id.delete(0, tk.END)
            self.addr_id.insert(0, values[0])
            self.supplier_id.delete(0, tk.END)
            self.supplier_id.insert(0, values[1])
            self.o_year.delete(0, tk.END)
            self.o_year.insert(0, values[2])
            self.o_month.delete(0, tk.END)
            self.o_month.insert(0, values[3])
            self.o_status.delete(0, tk.END)
            self.o_status.insert(0, values[4])
            self.o_issue_date.delete(0, tk.END)
            self.o_issue_date.insert(0, values[5])
            self.o_statement_total.delete(0, tk.END)
            self.o_statement_total.insert(0, values[6])


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

        self.sales_statement_tree = ttk.Treeview(tree_frame,
                                                 columns=('s_id', 'year', 'month', 'issue_date', 'S_Statement_total'),
                                                 show='headings')
        self.sales_statement_tree.heading('s_id', text='Sale ID')
        self.sales_statement_tree.heading('year', text='Year')
        self.sales_statement_tree.heading('month', text='Month')
        self.sales_statement_tree.heading('issue_date', text='Issue Date')
        self.sales_statement_tree.heading('S_Statement_total', text='Total')

        for col in ('s_id', 'year', 'month', 'issue_date', 'S_Statement_total'):
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
        year = self.sales_year.get()
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
        SELECT TOP (1000) s_id, year, month, issue_date, S_Statement_total
        FROM [project2].[dbo].[sales_monthly_statement]
        WHERE month = ? AND year = ?
        """
        sales = self.execute_db_operation(query, (month_number, year))
        self.sales_statement_tree.delete(*self.sales_statement_tree.get_children())
        if sales:
            for sale in sales:
                self.sales_statement_tree.insert('', 'end', values=sale)
        else:
            messagebox.showinfo("Info", "No sales found for the selected month and year.")

    def load_monthly_sales(self):
        query = """
        SELECT TOP (1000) s_id, year, month, issue_date, S_Statement_total
        FROM [project2].[dbo].[sales_monthly_statement]
        """
        sales = self.execute_db_operation(query)
        self.sales_statement_tree.delete(*self.sales_statement_tree.get_children())
        if sales:
            for sale in sales:
                self.sales_statement_tree.insert('', 'end', values=sale)

    def on_sales_statement_select(self, event):
        selected_item = self.sales_statement_tree.focus()
        if selected_item:
            values = self.sales_statement_tree.item(selected_item, 'values')
            # Additional actions can be implemented here if needed

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
