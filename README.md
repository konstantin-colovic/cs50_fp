# CS50x Final project

## Overall

The use of this web application is to enable users to see the menu prices of a certain restaurant, and potentially order something using the interactive ordering system, the application also consists of an admin profile where you can see the incoming orders, mark them as completed, or not.

## Usage

### User usage

##### Authentication

To use this web application the user would be prompted either to log in or to register for an account using their `username`, `password`, `address` and `email`.

There will be two pages:

1. Login page contains fields `username` and `password`
3. Register page contains fields `username`, `password`, `address` and `email`.

> Note: Address will be a unified field where users will enter their data


##### Ordering

After that the user could scroll through the menu options of the given restaurant and chose the items they wish to order, when the items are chosen, the final order can be viewed and either **confirmed** and sent to the restaurant, or it can be **canceled**.

##### E-mail notifying that order is done

Once the admin has marked the order as **done** the user that ordered the given order will recieve an email telling them that their order is done.

### Administrator usage

If the restaurant wants to see their orders, they can do so by logging in as the admin and viewing their orders, potentially marking them as done.

#### Preview orders

Table showing a list of orders contaning:

- `item list` ordered (comma separated),
- the `name` of the customer,
- the `sum` of the price, and the adresss

---

| Item list | Customer | Order Price | Address |
| -|-|-|-|
| Coffe, Pizza Large Peperoni, Icecream | John Cleese | 25.00$ | Johnson Ave. 12, Nuntucket |
| Coffe, Pizza Large Peperoni, Icecream | John Cleese | 25.00$ | Johnson Ave. 12, Nuntucket |
| Coffe, Pizza Large Peperoni, Icecream | John Cleese | 25.00$ | Johnson Ave. 12, Nuntucket |

#### Fullfill orders

Admin will **mark them as done** and they will be deleted.

#### Notes on admin usage

Decisions made before implementing:

> 1. No way to remove or delete order from the list aside from mark them as done
> 2. No way to view order previously marked as done