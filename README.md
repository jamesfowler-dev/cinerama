# Cinerama

### [⛓️ Click Here To see The Live Website](https://cinerama-project-c41e4c3cc388.herokuapp.com/)

![landing_gif.gif](static/readme/landing_gif.gif)

Cinerama is our awesome way of showcasing an ecommerce website.
From showing dynamic prices to having a manageable booking. Using TMBD API to show titles, posters, cast and more.
YouTube API to fetch appropriate trailers for the films and a Copilot API that creates age ratings.
This web app was a big package and lots of fun to work on. It has tons of room for improvement.
But even now, comparing it to other cinema websites we are quite happy with the design and logic behind it.

| **Collaborator** | responsible for:                 | linked-in                                                               | GitHub                                      |
|------------------|----------------------------------|-------------------------------------------------------------------------|---------------------------------------------|
| James Flower     | Project Lead / Full-Stack dev    | [James](https://www.linkedin.com/in/jamesfowler21/)                     | [James](https://github.com/jamesfowler-dev) |
| Amy Cartwright   | Full-Stack dev                   | [Amy](https://www.linkedin.com/in/amy-cartwright-624498279/)            | [Amy](https://github.com/AC-dev16)          |
| Thomas Clevely   | Full-Stack dev                   | [Thomas](https://www.linkedin.com/in/thomas-clevely-2a4289389/)         | [Thomas](https://github.com/Ruon90)         |
| Rafael Sanchez   | Ideation, Drafting and debugging | [Rafael](https://www.linkedin.com/in/rafael-horwood-sanchez-291914224/) | [Rafael](https://github.com/RH1945)         |

# Index

- [Overview](#overview)
- [UX Design](#ux-design)
- [User Stories](#user-stories)
- [ERD](#erd)
- [Colors](#colors)
- [Font](#font)
- [Key Features](#key-features)
- [User Authentication & Management](#user-authentication--management)
- [Data Management](#data-management)
- [Deployment](#deployment)
- [AI Implementation](#ai-implementation)
- [Testing](#testing)
    - [Desktop Lighthouse Reports](#desktop-lighthouse-reports)
    - [Mobile Lighthouse Reports](#mobile-lighthouse-reports)
    - [HTML Validation](#html-validation)
    - [CSS Validation](#css-validation)
    - [Python Validation](#python-validation)
    - [JavaScript Validation](#javascript-validation)
    - [Manual Testing](#manual-testing)
- [Future Enhancements](#future-enhancements)
- [Credits](#credits)

---

# Overview

---

# UX Design

---

### Templates

---

# User Stories

---

# ERD

<details>
<summary>
The Entity Relationship Diagrams (ERDs) are essential for defining the data structure,
relationships, and constraints within the Cinerama booking system.
They were designed early in the project to ensure consistency between the database,
business logic, and user interactions throughout the cinema booking flow. Read more...
</summary>
<br>

## Relationship Summary

| From     | To          | Relationship | On Delete |
|----------|-------------|--------------|-----------|
| Screen   | Seat        | One-to-Many  | CASCADE   |
| Screen   | Showtime    | One-to-Many  | CASCADE   |
| Film     | Showtime    | One-to-Many  | CASCADE   |
| Showtime | Booking     | One-to-Many  | CASCADE   |
| User     | Booking     | One-to-Many  | CASCADE   |
| Booking  | BookingSeat | One-to-Many  | CASCADE   |
| Seat     | BookingSeat | One-to-Many  | CASCADE   |

### ERD Cardinality Overview

- Screen
    - ├── 0..* Seat
    - └── 0..* Showtime
- Film
    - └── 0..* Showtime
- Showtime
    - └── 0..* Booking
- User
    - └── 0..* Booking
- Booking
    - └── 0..* BookingSeat
- Seat
    - └── 0..* BookingSeat

---

<details>
<summary>Screen</summary>
<br>

| Field Name | Type         | Constraints        | Description                          |
|------------|--------------|--------------------|--------------------------------------|
| id         | AutoField    | PK                 | Unique screen identifier             |
| type       | IntegerField | choices, default=0 | Screen type (Silver, IMAX, VIP etc.) |
| number     | IntegerField | required           | Screen number                        |
| seats      | IntegerField | required           | Total number of seats                |

**Notes:**

- `type` and `number` are unique together to prevent duplicate screens.

</details>

<details>
<summary>Film</summary>
<br>

| Field Name     | Type            | Constraints            | Description               |
|----------------|-----------------|------------------------|---------------------------|
| id             | AutoField       | PK                     | Unique film identifier    |
| title          | CharField       | required               | Film title                |
| director       | CharField       | required               | Film director             |
| cast           | TextField       | required               | Main cast members         |
| year           | DateField       | required               | Release year              |
| duration       | IntegerField    | required               | Duration in minutes       |
| rating         | CharField       | choices, default=PG    | Age rating                |
| genre          | CharField       | choices, default=drama | Film genre                |
| synopsis       | TextField       | optional               | Film synopsis             |
| poster_url     | CharField       | optional               | Poster image URL          |
| backdrop_url   | CharField       | optional               | Backdrop image URL        |
| trailer_url    | URLField        | optional               | Trailer video URL         |
| tmdb_id        | PositiveInteger | unique, optional       | External TMDB reference   |
| is_new_release | BooleanField    | default=True           | New release flag          |
| is_classic     | BooleanField    | default=False          | Classic film flag         |
| is_active      | BooleanField    | default=True           | Active listing status     |
| created_at     | DateTimeField   | auto                   | Record creation timestamp |
| updated_at     | DateTimeField   | auto                   | Last update timestamp     |

</details>

<details>
<summary>Showtime</summary>
<br>

| Field Name   | Type                | Constraints  | Description                |
|--------------|---------------------|--------------|----------------------------|
| id           | AutoField           | PK           | Unique showtime identifier |
| film         | ForeignKey → Film   | CASCADE      | Film being shown           |
| screen       | ForeignKey → Screen | CASCADE      | Screen used for showing    |
| date         | DateField           | required     | Showtime date              |
| time         | TimeField           | required     | Showtime time              |
| price        | DecimalField        | required     | Ticket price               |
| is_available | BooleanField        | default=True | Availability status        |

**Notes:**

- Screen, date, and time are unique together to avoid scheduling conflicts.
- Available seats are calculated dynamically.

</details>

<details>
<summary>Seat</summary>
<br>

| Field Name | Type                | Constraints | Description                        |
|------------|---------------------|-------------|------------------------------------|
| id         | AutoField           | PK          | Unique seat identifier             |
| screen     | ForeignKey → Screen | CASCADE     | Screen this seat belongs to        |
| row        | CharField           | required    | Seat row (A, B, C...)              |
| number     | IntegerField        | required    | Seat number                        |
| seat_type  | CharField           | default     | Standard, premium, wheelchair etc. |

**Notes:**

- Seats are uniquely identified by screen, row, and number.

</details>

<details>
<summary>Booking</summary>
<br>

| Field Name     | Type                  | Constraints      | Description                 |
|----------------|-----------------------|------------------|-----------------------------|
| id             | AutoField             | PK               | Internal booking identifier |
| booking_id     | UUIDField             | unique           | Public booking reference    |
| user           | ForeignKey → User     | CASCADE          | Booking owner               |
| showtime       | ForeignKey → Showtime | CASCADE          | Showtime booked             |
| booking_date   | DateTimeField         | auto             | Booking timestamp           |
| total_price    | DecimalField          | required         | Total booking price         |
| status         | CharField             | choices, default | Booking status              |
| payment_method | CharField             | optional         | Payment method used         |

</details>

<details>
<summary>BookingSeat</summary>
<br>

| Field Name | Type                 | Constraints | Description                    |
|------------|----------------------|-------------|--------------------------------|
| id         | AutoField            | PK          | Unique booking-seat identifier |
| booking    | ForeignKey → Booking | CASCADE     | Associated booking             |
| seat       | ForeignKey → Seat    | CASCADE     | Reserved seat                  |
| price      | DecimalField         | required    | Seat price                     |

**Notes:**

- Each seat can only be booked once per booking.

</details>

This was the first sketch for the ERDs:
![ERD.png](static/readme/ERD.png)

</details>


---

# Colors

---

# Font

---

# Key Features

---

# User Authentication & Management

---

# Data Management

---

# Deployment

---

# AI Implementation

---

# Testing

---

# Desktop Lighthouse Reports

---

# Mobile Lighthouse Reports

---

# HTML Validation

---

# CSS Validation

---

# Python Validation

---

# JavaScript Validation

---

# Manual Testing

---

# Future Enhancements

---

# Credits



