# Parking Lot Management System

## Install
See [docs/install.md](docs/install.md) for details.

## Abstract

There is an expanding firm in business of multi-storey parking lots. This firm owns one parking lot at the moment, yet looking for an opportunity to expand, therefore is in need for a system to manage all parking lots it owns at once.

This system stores and monitor firm details, costumer informations, parking lots' informations, usage rates, accounting data; and allow users to manage the lots or their membership information.

## Detailed Information

Parking lot(s) have parking spots for cars, motorcycles and bikes. They also have charging spots for electrical cars and electrical motorcycles. Parking lot(s) may have couple areas designated to be rented to 3rd party entrepreneurs for small shops like car wash, café or lounge. 

While entering the parking lot, information of total number of empty spots on that very floor and floors above or below for each vehicle type should be given to the driver, biker or cyclist. This information should be updated real-time. Usage information (occupancy ratio) per hour per day of the whole parking lot should be kept at the database for at least three months, so this data can be used to show statistics of usage ratio.

### Parking
Parking spots will have a parking meter per spot. They will;
   - be able to detect parked vehicle,
   - be able to read vehicle plate number,
   - have NFC to reach customer memberships and wallet account,
   - be able to accept credit card and cash.
Parking fees may vary from one parking lot to another. For base prices see Table 1.

| Vehicle    | Starting Fee       | Added Fee (after one hour) |
|------------|:------------------:|:--------------------------:|
| Car        |         $2         |             $1             |
| Motorcycle |        $0.80       |            $0.30           |

*Table 1: Base Prices for parking. All prices are per hour.*

### Charging
Charging spots must not occupied more than 10 minutes after the vehicle is fully charged. For every additional minute a vehicle remains connected to the charging spot, it will incur a idle fee. If the vehicle is moved within 10 minutes, the fee is waived.
Two notifications should be send to the owner of the electrical vehicle, 15 minute prior to full charge and when the vehicle is fully charged.
Charging fees and idle fees may vary from one parking lot to another. For base prices see Table 2.

| Vehicle    | Charging Fee (Tier 1) | Charging Fee (Tier 2) | Idle Fee |
|------------|:---------------------:|:---------------------:|:--------:|
| Car        |         $0.07         |         $0.05         |   $0.30  |
| Motorcycle |         $0.05         |         $0.04         |   $0.15  |

*Table 2: Base Prices for charging vehicles. All prices are per minute.*


|        | Car charges | Motorcycle chargers |
|--------|-------------|---------------------|
| Tier 1 | From 60 kW  | From 12 kW          |
| Tier 2 | Up to 60 kW | Up to 12 kW         |

*Table 3: Charging fee profiles.*

### Membership Options

The firm have membership options for customers. There are two packages for membership.

1. First package allows a customer to get a discount for a number of vehicles at any parking lots the firm own at the same time. 
   1. Discount percentage increases as the number of vehicle included in that package increases. 

   2. Maximum number of vehicles per member is capped at 3. 

   3. There is a monthly fee for the membership which increases as allowed number of vehicle increases. 
See Table 4 for details.

2. Second package allows a customer to rent a fixed spot for a single registered vehicle.
   1. Rented spot will only be available to only and only that member.

   2. Rented spot is vehicle specified. No other vehicle than predefined one can use the spot.

   3. The member may change the vehicle that will be able to use the spot. One change per three months.

   4. An empty rented spot will not be counted in empty spots available to common members.

   5. Prices for this package may vary from one parking lot to another.

   6. A member may sign-up for more than one spot. 

See Table 5 for details.


| # of vehicles | Discount | Monthly fee |
|:-------------:|:--------:|:-----------:|
|       1       |  **10%** |     $15     |
|       2       |  **15%** |     $25     |
|       3       |  **20%** |     $30     |

*Table 4: Discount package details*


| Vehicle    | Base price (monthly) | Base price (annually) |
|------------|:--------------------:|:---------------------:|
| Car        |          $80         |          $800         |
| Motorcycle |          $30         |          $300         |

*Table 5: Rental parking spot price table*

Each member will be given at least one card that will help him/her identify self to parking meter.
Members having a card will have a wallet account. They should be able to add a credit card to their wallet accounts. Credit card info should be kept encrypted. CVC info of each card should be kept in a different table where all other info of credit card is being stored. Last 4 digit of a credit card may be stored openly.

### Payment

1. (Optional) Member reads his/her card to parking/charging meter prior to parking/charging.
   1. If there is free slot available for discounted parking, occupy a slot.
   2. Else, inform the member, start parking/charging at normal price rate.

2. Parking/charging meter calculates the cost to be paid.

3. Customer have three options to pay:
   1. With cash
      - Machine accepts money.
      - Gives change if necessary.
      - Gives receipt.

   2. With credit card
      - Establish a secure connection to card provider.
      - Read card info and query that info with requested fee.
      - If the card is charged, give receipt; otherwise ask for another payment method.

   3. (Optional) With member wallet account
      - Member makes machine read the card.
      - Read if this spot was occupied for discounted parking, if so apply discount.
      - Establish a secure connection to card provider.
      - Query saved card info with requested fee.
      - If the card is charged, give receipt; otherwise ask for another payment method.

4. Save revenue instance information to database with following information:
   - Date and duration of parking
   - Parking lot info
   - Parking/charging spot info
   - Revenue
   - Payment method
   - (Optional) Electricity used 
   - (Optional) Idle fee

### Financial Tables

These break down revenue and profit information for different categories. Tables show revenue from memberships, rentals, parking fees, charging fees etc.P

### Users of the system

There are several types of users with varying authorizations. 

   - **Super User(SU)**: 
   Can access every data but credit card information, can edit every data. Can reach lot management, membership management, finance management panels. Add/drop administrators.
   - **Administrator**: 
   Can access every data but credit card informations. Can reach lot management, membership management, finance management panels. 
   - **Corporate user**: 
   Can reach finance management panels. Add/drop members. Change membership 
   - **Member**: 
   Can access his/her membership details, change credit card information, look for past usage.
   - **Common user**: 
   Doesn't have any credentials. Can start a membership. Can see only the landing page of the website and get information about:
      - Live usage information
      - Membership opportunities
