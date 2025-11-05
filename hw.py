from collections import UserDict
from datetime import datetime, timedelta #, to_datetime
import pickle

def save_data(book, filename="addressbook.pkl"):
    try:
        with open(filename, "wb") as f:
            pickle.dump(book, f)
    except Exception as e:
        print(f"Error saving data: {e}")
        raise

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено
    except (pickle.UnpicklingError, EOFError, ValueError) as e:
        print(f"Error loading data: {e}. Creating new address book.")
        return AddressBook()  # Повернення нової адресної книги, якщо файл пошкоджений


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
    def __init__(self, value):
         if not value.strip():  # Перевірка на порожній рядок після видалення пробілів
            raise ValueError("Name cannot be empty")
         super().__init__(value)
		

class Phone(Field):
    # реалізація класу
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits and contain only numbers")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        if not value.strip():  # Перевірка на порожній рядок після видалення пробілів
            raise ValueError("Birthday cannot be empty")
        try:
            # Перетворення рядка DD.MM.YYYY на об'єкт datetime.date
            parsed_date = datetime.strptime(value.strip(), '%d.%m.%Y').date()
            super().__init__(parsed_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def edit_phone(self, old_number, new_number):
        new_phone = Phone(new_number)  # Перевірить валідацію
        for i, phone in enumerate(self.phones):
            if phone.value == old_number:
                self.phones[i] = new_phone
                return
        raise ValueError("Old phone number not found")
    
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def delete_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return
        raise ValueError("Phone number not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        return f"Birthday added: {self.birthday.value.strftime('%d.%m.%Y')}"
    
    def show_birthday(self):
        if self.birthday is None:
            return "Birthday not set"
        return f"{self.birthday.value.strftime('%d.%m.%Y')}"



class AddressBook(UserDict):
    # реалізація класу
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")
        
    def find(self, name):
        return self.data.get(name, None)

    def add_birthday(self, name, birthday):
        record = self.find(name)
        if record:
            record.add_birthday(birthday)
        else:
            raise ValueError("Record not found")

    def show_birthday(self, name):
        record = self.find(name)
        if record:
            return record.show_birthday()
        else:
            raise ValueError("Record not found")
    
    def birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for name, record in self.data.items():
            if record.birthday is None:
                continue
            try:
                birth_date = record.birthday.value
                this_year_birthday = birth_date.replace(year=today.year)

                if this_year_birthday < today:
                    this_year_birthday = birth_date.replace(year=today.year + 1)
                
                delta_days = (this_year_birthday - today).days
                if 0 <= delta_days <= 7:
                    celebration_date = this_year_birthday
                    if celebration_date.weekday() in (5, 6):  # Saturday or Sunday
                        celebration_date += timedelta(days=(7 - celebration_date.weekday()))
                    upcoming.append({"name": name, "celebration_date": celebration_date.strftime('%d.%m.%Y')})
            except (ValueError, AttributeError):
                continue
        return upcoming


# decorator для обробки помилок введення користувача
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "This contact does not exist."
        except IndexError:
            return "Error: Please provide contact name. Usage: phone <name>"
       
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args  # ValueError автоматично
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found")
    record.edit_phone(old_phone, new_phone)
    return f"Contact '{name}' updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]  # IndexError автоматично, якщо список порожній
    record = book.find(name)
    if record:
        if not record.phones:
            return f"{name} has no phone numbers."
        phones_str = "; ".join(phone.value for phone in record.phones)
        return f"{name}: {phones_str}"
    else:
        raise KeyError("Contact not found")

def show_all_contacts(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found")
    result = record.add_birthday(birthday)
    return result

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    return f"{name}: {book.show_birthday(name)}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    result = "Upcoming birthdays:\n"
    for item in upcoming:
        result += f"{item['name']}: {item['celebration_date']}\n"
    return result.strip()

def main():
    book = load_data()
    # book = AdressBook()
    print("Welcome to the assistant bot!\nType 'help' for available commands.")
    try:
        while True:
            user_input = input("Enter a command: ")
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                save_data(book)
                print("Good bye!")           
                break
            elif command == "help":
                print("Available commands:\n"
                  "add <name> <phone> - Add a new contact\n"
                  "change <name> <old_phone> <new_phone> - Change an existing contact's phone number\n"
                  "phone <name> - Show the phone number of a contact\n"
                  "all - Show all contacts\n"
                  "add-birthday <name> <birthday> - Add a birthday to a contact (format: DD.MM.YYYY)\n"
                  "show-birthday <name> - Show the birthday of a contact\n"
                  "birthdays - Show upcoming birthdays in the next week\n"
                  "hello - Get greeting from bot\n"
                  "close/exit - Exit the program\n"
                  "help - Show this help message")
            elif command == "hello":
                print("How can I help you?")
            elif command == "add":
                print(add_contact(args, book))
            elif command == "change":
                print(change_contact(args, book))
            elif command == "phone":
                print(show_phone(args, book))
            elif command == "all":
                print(show_all_contacts(book))
            elif command == "add-birthday":
                print(add_birthday(args, book))
            elif command == "show-birthday":
                print(show_birthday(args, book))
            elif command == "birthdays":
                print(birthdays(args, book))
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        print("\nProgram interrupted. Saving data...")
        save_data(book)
        print("Good bye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}. Saving data...")
        save_data(book)
        raise

if __name__ == "__main__":
    main()