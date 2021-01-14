import sqlite3
import config as cfg
from utility import reporting as rprt


class Database(object):
    """docstring for Database"""
    backed = False

    def __init__(self, file):
        super(Database, self).__init__()
        self.file_path = file
        self.file = str(file)

    def create(self, clean=True):
        message = 'DATABASE is being created.'
        rprt.report(init, message, self.file, clean=clean)

    def __backup(self):
        ''' Backs up the database at the same directory '''
        def backup(obj):
            ''' a temporary local function
            Pass 'self' variable of Database object to backup's obj
                e.g. backup(obj=self)'''
            from shutil import copy
            backup_path = obj.file_path.with_suffix('.db.bak')
            obj.file_path.replace(backup_path)
            copy(backup_path, obj.file_path)
            obj.backed = True
        message = 'DATABASE is backing up.'
        rprt.report(backup, message, obj=self)

    def __restore(self):
        ''' Restores backed up file to its original location '''
        def __restore_temp(obj):
            if obj.backed:
                obj.file_path.unlink()
                backup_path = obj.file_path.with_suffix('.db.bak')
                backup_path.replace(obj.file_path)
            else:
                return 'ABORTED'
        message = 'DATABASE is restoring from backup.'
        rprt.report(__restore_temp, message, obj=self)

    def test(self, verbose=False):
        rprt.report_at_once('TESTING started.', 'OK')
        self.__backup()  # Backup database
        try:
            from tests import firm
            import unittest

            # Get every test suites in .py files in module /tests
            test_suites = []
            test_suites.append(unittest.TestLoader().loadTestsFromModule(firm))

            # Create an object to run the tests
            if verbose:
                test_runner = unittest.TextTestRunner(verbosity=2)
            else:
                test_runner = unittest.TextTestRunner()

            # Run each test suite
            for suite in test_suites:
                test_runner.run(suite)
        except Exception as e:
            raise e
        finally:
            self.__restore()  # Restore the backup
        rprt.report_at_once(
            'TESTING completed. Read above for the results.', 'OK')

    def populate(self):
        fill_tables_demo(self.file)


def init(file, clean=True, verbose=False):
    c = open(file)
    if clean:
        delete_tables(c)
    # create Firm table
    Firm_sql = "CREATE TABLE Firm(\
        'FirmAlias'     TEXT\
            PRIMARY KEY\
            UNIQUE\
            CHECK (length(FirmAlias) > 0 and length(FirmAlias) <= 5)\
            NOT NULL,\
        'FirmName'      TEXT\
            UNIQUE\
            NOT NULL,\
        'URL'           TEXT\
            UNIQUE\
            CHECK (lower(URL) LIKE '_%._%'),\
        'EMail'         TEXT\
            UNIQUE\
            CHECK (lower(EMail) LIKE '_%@_%._%'),\
        'Telephone'     TEXT\
            UNIQUE,\
        'Street_1'      TEXT,\
        'Street_2'      TEXT,\
        'City'          TEXT,\
        'Region'        TEXT,\
        'PostalCode'    TEXT\
            CHECK (length(PostalCode) <= 8)\
        )"
    execute(Firm_sql, c)

    # create ParkingLots
    ParkingLots_sql = "CREATE TABLE ParkingLots(\
        'LotAlias'          TEXT\
            PRIMARY KEY\
            UNIQUE\
            NOT NULL,\
        'FirmAlias'         TEXT\
            REFERENCES Firm(FirmAlias)\
            NOT NULL,\
        'LotName'           TEXT\
            UNIQUE\
            NOT NULL,\
        'PriceMultiplier'   REAL\
            NOT NULL,\
        'Street_1'          TEXT,\
        'Street_2'          TEXT,\
        'City'              TEXT,\
        'Region'            TEXT,\
        'PostalCode'        TEXT)"
    execute(ParkingLots_sql, c)

    # create table Floors
    Floors_sql = "CREATE TABLE Floors(\
        'FloorID'       TEXT\
            PRIMARY KEY\
            UNIQUE\
            NOT NULL,\
        'FloorNumber'   TEXT\
            NOT NULL,\
        'LotAlias'      TEXT\
            REFERENCES ParkingLots(LotAlias))"
    execute(Floors_sql, c)

    # create table RentalAreas
    Rental_Areas_sql = "CREATE TABLE RentalAreas(\
       'RentalID'       TEXT\
            PRIMARY KEY\
            UNIQUE\
            NOT NULL,\
       'FloorNumber'    TEXT\
            REFERENCES Floors(FloorNumber)\
            NOT NULL,\
        'LotAlias'      TEXT\
            REFERENCES Floors(LotAlias))"
    execute(Rental_Areas_sql, c)

    # create table ChargeSpots
    Charge_spots_sql = "CREATE TABLE ChargeSpots(\
       'CSpotID'        TEXT\
            PRIMARY KEY\
            UNIQUE\
            NOT NULL,\
       'LotAlias'       TEXT\
            REFERENCES Floors(LotAlias),\
        'FloorNumber'   TEXT\
            REFERENCES Floors(FloorNumber))"
    execute(Charge_spots_sql, c)

    # create table ParkingSpots
    Parking_Spots_sql = "CREATE TABLE ParkingSpots(\
        'PSpotID'       TEXT\
            PRIMARY KEY\
            NOT NULL,\
        'LotAlias'      TEXT\
            REFERENCES ChargeSpots(LotAlias),\
         'FloorNumber'  TEXT\
            REFERENCES Floors(FloorNumber)\
            NOT NULL)"
    execute(Parking_Spots_sql, c)

    # create table ReservedSpots
    Reserved_Spots_sql = "CREATE TABLE ReservedSpots(\
        'PSpotID'       TEXT\
            REFERENCES ParkingSpots(PSpotID)\
            NOT NULL,\
        'MShipNum'      TEXT\
            REFERENCES MembershipRentals(MshipNum)\
            NOT NULL,\
        PRIMARY KEY('PSpotID', 'MShipNum'))"
    execute(Reserved_Spots_sql, c)

    # create table RentalAgreements
    Rental_Agreement_sql = "CREATE TABLE RentalAgreement(\
        'RentalID'      TEXT\
            REFERENCES RentalAreas(RentalID)\
            NOT NULL,\
        'LotAlias'      TEXT\
            REFERENCES RentalAreas(LotAlias)\
            UNIQUE,\
        'TenandID'      TEXT\
            REFERENCES RentalAreas(TenandID)\
            UNIQUE,\
        'StartDate'     TEXT\
            NOT NULL,\
        'EndDate'       TEXT\
            NOT NULL,\
        'Rent'         TEXT\
            NOT NULL,\
        'Duration'      INTEGER\
            NOT NULL,\
        'Description'   TEXT\
            NOT NULL,\
        PRIMARY KEY(RentalID ,'LotAlias','TenandID'))"
    execute(Rental_Agreement_sql, c)

    # create table TenantContacts
    Tenant_Contacts_sql = "CREATE TABLE TenantContacts(\
        'TenantID'      TEXT\
            PRIMARY KEY\
            NOT NULL,\
        'Name'          TEXT\
            NOT NULL,\
        'Telephone'     TEXT\
            NOT NULL,\
        'EMail'         TEXT\
            NOT NULL)"
    execute(Tenant_Contacts_sql, c)

    # create table ChargingInfo
    Charging_info_sql = "CREATE TABLE ChargingInfo(\
        'CSpotID'       TEXT\
            PRIMARY KEY\
            REFERENCES ChargeSpots(CSpotID)\
            NOT NULL,\
        'StartedAt'     TEXT\
            NOT NULL,\
        'CPercentage'   TEXT\
            NOT NULL,\
        'CPower'        TEXT\
            NOT NULL,\
        'ChargeAt'      TEXT\
            NOT NULL)"
    execute(Charging_info_sql, c)

    # create table ParkingInfo
    Parking_info_sql = "CREATE TABLE ParkingInfo(\
        'PSpotID'       TEXT\
            PRIMARY KEY\
            REFERENCES ParkingSpots(PSpotID)\
            NOT NULL,\
        'StartedAt'     TEXT\
            NOT NULL)"
    execute(Parking_info_sql, c)

    # create table Users
    users_sql = "CREATE TABLE Users\
        (\
            'UserID'    TEXT\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT REPLACE\
                UNIQUE\
                    ON CONFLICT REPLACE\
                NOT NULL,\
            'UserName'  TEXT\
                UNIQUE\
                    ON CONFLICT REPLACE\
                NOT NULL,\
            'EMail'     TEXT\
                UNIQUE\
                    ON CONFLICT ABORT\
        )"
    execute(users_sql, c)

    # create table UsersCreditentials
    users_creditentials_sql = "CREATE TABLE UsersCreditentials\
        (\
            'UserID'        TEXT\
                PRIMARY KEY\
                REFERENCES Users(UserID)\
                NOT NULL,\
            'Password'  TEXT\
                NOT NULL\
        )"
    execute(users_creditentials_sql, c)

    # create table Permissions
    permissions_sql = "CREATE TABLE Permissions\
        (\
            'PermissionKey' TEXT\
                PRIMARY KEY,\
            'Description'   TEXT\
        )"
    execute(permissions_sql, c)

    # create table UserPermissions
    user_permissions_sql = "CREATE TABLE UserPermissions\
        (\
            'UserID'        TEXT\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT REPLACE\
                REFERENCES Users(UserID)\
                NOT NULL,\
            'PermissionKey' TEXT\
                REFERENCES Permissions(PermissionKey)\
                NOT NULL\
        )"
    execute(user_permissions_sql, c)

    # create table Members
    members_sql = "CREATE TABLE Members\
        (\
            'MemberID'      TEXT\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT ROLLBACK\
                UNIQUE\
                NOT NULL,\
            'UserID'        TEXT\
                REFERENCES Users(UserID)\
                NOT NULL,\
            'MemberName'    TEXT\
                NOT NULL\
        )"
    execute(members_sql, c)

    # create table WalletAccounts
    wallet_accounts_sql = "CREATE TABLE WalletAccounts\
        (\
            'WalletID'      TEXT\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT ROLLBACK\
                UNIQUE\
                    ON CONFLICT ROLLBACK\
                NOT NULL,\
            'MemberID'      TEXT\
                REFERENCES Members(MemberID)\
                UNIQUE\
                NOT NULL\
        )"
    execute(wallet_accounts_sql, c)

    # Create table CreditCards
    credit_cards_sql = "CREATE TABLE CreditCards\
        (\
            'CardID'        TEXT\
                PRIMARY KEY\
                    ON CONFLICT ROLLBACK\
                UNIQUE\
                    ON CONFLICT ROLLBACK\
                NOT NULL,\
            'WalletID'      TEXT\
                REFERENCES WalletAccounts(WalletID),\
            'HolderName'    TEXT\
                NOT NULL,\
            'ValidUntil'    TEXT\
                NOT NULL\
        )"
    execute(credit_cards_sql, c)

    # Create table CardQuartets
    card_quartets_sql = "CREATE TABLE CardQuartets\
        (\
            'CardID'        TEXT\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT REPLACE\
                REFERENCES CreditCards(CardID)\
                NOT NULL,\
            'CardQ1'        TEXT\
                NOT NULL,\
            'CardQ2'        TEXT\
                NOT NULL,\
            'CardQ3'        TEXT\
                NOT NULL,\
            'CardQ4'        TEXT\
                NOT NULL\
        )"  # Save 1st, 2nd, 3rd quartets encrypted, leave 4th as it is
    execute(card_quartets_sql, c)

    # create table Memberships
    memberships_sql = "CREATE TABLE Memberships\
        (\
            'MShipNum'      TEXT\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT ROLLBACK\
                UNIQUE\
                NOT NULL,\
            'MemberID'      TEXT\
                REFERENCES Members(MemberID)\
                NOT NULL,\
            'Type'          TEXT,\
            'StartDate'     TEXT,\
            'EndDate'       TEXT,\
            'Duration'      INTEGER,\
            'Price'         REAL\
        )"
    execute(memberships_sql, c)

    # create table MembershipRentals
    membership_rentals_sql = "CREATE TABLE MembershipRentals\
        (\
            'MShipNum'      TEXT\
                PRIMARY KEY\
                    ON CONFLICT ROLLBACK\
                REFERENCES Memberships(MShipNum)\
                NOT NULL,\
            'RentalType'    INTEGER\
                REFERENCES Rentals(RentalType)\
        )"
    execute(membership_rentals_sql, c)

    # create table Rentals
    rentals_sql = "CREATE TABLE Rentals\
        (\
            'RentalType'    INTEGER\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT REPLACE\
                    AUTOINCREMENT\
                UNIQUE\
                    ON CONFLICT REPLACE\
                NOT NULL,\
            'VehicleType'   TEXT\
                CHECK(VehicleType = 'Car' or VehicleType = 'Motorcycle')\
                NOT NULL,\
            'RentalTerm'    TEXT\
                CHECK(RentalTerm = 'Monthly' or RentalTerm = 'Annual')\
                NOT NULL,\
            'BaseFee'       INTEGER\
                NOT NULL\
        )"
    execute(rentals_sql, c)

    # create table MembershipDiscounts
    membership_discounts_sql = "CREATE TABLE MembershipDiscounts\
        (\
            'MShipNum'      TEXT\
                PRIMARY KEY\
                REFERENCES Memberships(MShipNum)\
                UNIQUE\
                NOT NULL,\
            'VehicleCount'  INTEGER\
                CHECK(1 or 2 or 3)\
                REFERENCES Discounts(VehicleCount)\
        )"
    execute(membership_discounts_sql, c)

    # create table Discounts
    discounts_sql = "CREATE TABLE Discounts\
        (\
            'VehicleCount'  INTEGER\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT REPLACE\
                UNIQUE\
                    ON CONFLICT REPLACE\
                CHECK(1 or 2 or 3)\
                NOT NULL,\
            'Discounts'     REAL\
                NOT NULL\
        )"
    execute(discounts_sql, c)

    # create table ParkingPrices
    parking_prices_sql = "CREATE TABLE ParkingPrices\
        (\
            'VehicleType'   TEXT\
                PRIMARY KEY\
                    ON CONFLICT REPLACE\
                UNIQUE\
                    ON CONFLICT REPLACE\
                CHECK(VehicleType = 'Car' or VehicleType = 'Motorcycle')\
                NOT NULL,\
            'StartingFee'   REAL\
                NOT NULL,\
            'ExtraFee'      REAL\
                NOT NULL\
        )"
    execute(parking_prices_sql, c)

    # create table ChargingPrices
    charging_prices_sql = "CREATE TABLE ChargingPrices\
        (\
            'VehicleType'   TEXT\
                PRIMARY KEY\
                    ON CONFLICT REPLACE\
                UNIQUE\
                    ON CONFLICT REPLACE\
                CHECK(VehicleType = 'Car' or VehicleType = 'Motorcycle')\
                NOT NULL,\
            'ChargingFeeT1' REAL\
                NOT NULL,\
            'ChargingFeeT2' REAL\
                NOT NULL,\
            'IdleFee'       REAL\
                NOT NULL\
        )"
    execute(charging_prices_sql, c)

    # create table ChargerTiers
    charger_tier_profiles_sql = "CREATE TABLE ChargerTiers\
        (\
            'ProfileNumber'     INTEGER\
                PRIMARY KEY\
                    ASC\
                    ON CONFLICT REPLACE\
                    AUTOINCREMENT\
                UNIQUE\
                    ON CONFLICT REPLACE,\
            'Tier'              INTEGER\
                UNIQUE\
                    ON CONFLICT REPLACE\
                CHECK(1 or 2)\
                NOT NULL,\
            'VehicleType'       TEXT\
                CHECK(VehicleType = 'Car' or VehicleType = 'Motorcycle')\
                NOT NULL,\
            'LowerBound'        REAL\
                NOT NULL,\
            'UpperBound'        REAL\
                NOT NULL\
        )"
    execute(charger_tier_profiles_sql, c)

    user_view_sql = "CREATE VIEW user_info AS\
        SELECT Users.UserID, UserName, EMail, Password, PermissionKey\
        FROM Users\
            INNER JOIN UsersCreditentials\
                ON Users.UserID = UsersCreditentials.UserID\
            INNER JOIN UserPermissions\
                ON Users.UserID = UserPermissions.UserID;"
    execute(user_view_sql, c)

    '''rental_areas_view_sql = "SELECT\
        ParkingLots.LotAlias,\
        LotName,\
        Floors.FloorNumber,\
        RentalID FROM ParkingLots INNER JOIN Floors ON ParkingLots.LotAlias = Floors.LotAlias INNER JOIN RentalAreas ON ParkingLots.LotAlias = RentalAreas.LotAlias;"
    '''

    lots_floors_sql = "CREATE VIEW lots_floors AS\
        SELECT ParkingLots.LotAlias, LotName, PriceMultiplier, Floors.FloorID, FloorNumber\
        FROM ParkingLots\
        INNER JOIN Floors\
            ON ParkingLots.LotAlias = Floors.LotAlias;"
    execute(lots_floors_sql, c)
    fill_tables(conn=c, verbose=verbose)
    c.close()


def open(file):
    conn = sqlite3.connect(str(file))
    return conn


def execute(sql, conn):
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


def delete_tables(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Firm")
    cursor.execute("DROP TABLE IF EXISTS ParkingLots")
    cursor.execute("DROP TABLE IF EXISTS Floors")
    cursor.execute("DROP TABLE IF EXISTS RentalAreas")
    cursor.execute("DROP TABLE IF EXISTS ChargeSpots")
    cursor.execute("DROP TABLE IF EXISTS ParkingSpots")
    cursor.execute("DROP TABLE IF EXISTS ReservedSpots")
    cursor.execute("DROP TABLE IF EXISTS RentalAgreement")
    cursor.execute("DROP TABLE IF EXISTS TenantContacts")
    cursor.execute("DROP TABLE IF EXISTS ChargingInfo")
    cursor.execute("DROP TABLE IF EXISTS ParkingInfo")
    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("DROP TABLE IF EXISTS UsersCreditentials")
    cursor.execute("DROP TABLE IF EXISTS Permissions")
    cursor.execute("DROP TABLE IF EXISTS UserPermissions")
    cursor.execute("DROP TABLE IF EXISTS Members")
    cursor.execute("DROP TABLE IF EXISTS WalletAccounts")
    cursor.execute("DROP TABLE IF EXISTS CreditCards")
    cursor.execute("DROP TABLE IF EXISTS CardQuartets")
    cursor.execute("DROP TABLE IF EXISTS Memberships")
    cursor.execute("DROP TABLE IF EXISTS MembershipRentals")
    cursor.execute("DROP TABLE IF EXISTS Rentals")
    cursor.execute("DROP TABLE IF EXISTS MembershipDiscounts")
    cursor.execute("DROP TABLE IF EXISTS Discounts")
    cursor.execute("DROP TABLE IF EXISTS ChargingPrices")
    cursor.execute("DROP TABLE IF EXISTS ParkingPrices")
    cursor.execute("DROP TABLE IF EXISTS ChargerTiers")
    cursor.execute("DROP VIEW IF EXISTS user_info")
    cursor.execute("DROP VIEW IF EXISTS lots_floors")
    conn.commit()


def fill_tables(conn, verbose=False):
    queries = (
        "INSERT INTO Discounts VALUES (1, 0.10)",
        "INSERT INTO Discounts VALUES (2, 0.15)",
        "INSERT INTO Discounts VALUES (3, 0.20)",
        "INSERT INTO Rentals VALUES (1, 'Car', 'Monthly', 80)",
        "INSERT INTO Rentals VALUES (2, 'Car', 'Annual', 800)",
        "INSERT INTO Rentals VALUES (3, 'Motorcycle', 'Monthly', 30)",
        "INSERT INTO Rentals VALUES (4, 'Motorcycle', 'Annual', 300)",
        "INSERT INTO ChargingPrices VALUES('Car', 0.07, 0.05, 0.30)",
        "INSERT INTO ChargingPrices VALUES('Motorcycle', 0.05, 0.04, 0.15)",
        "INSERT INTO ParkingPrices VALUES('Car', 2, 1)",
        "INSERT INTO ParkingPrices VALUES('Motorcycle', 0.80, 0.30)",
        "INSERT INTO ChargerTiers VALUES(1, 1, 'Car', 60, 999)",
        "INSERT INTO ChargerTiers VALUES(2, 1, 'Motorcycle', 12, 999)",
        "INSERT INTO ChargerTiers VALUES(3, 2, 'Car', 60, 60)",
        "INSERT INTO ChargerTiers VALUES(4, 2, 'Motorcycle', 0, 12)",
        "INSERT INTO Permissions VALUES(0, \
                '(00000) No permissions')",
        "INSERT INTO Permissions VALUES(1, \
                '(00001) Only member permissions')",
        "INSERT INTO Permissions VALUES(2, \
                '(00010) Only tenant permission')",
        "INSERT INTO Permissions VALUES(3, \
                '(00011) Tenant+Member permissions')",
        "INSERT INTO Permissions VALUES(4, \
                '(00100) Only Manager permissions')",
        "INSERT INTO Permissions VALUES(5, \
                '(00101) Manager+Member')",
        "INSERT INTO Permissions VALUES(6, \
                '(00110) Manager+Tenant')",
        "INSERT INTO Permissions VALUES(7, \
                '(00111) Manager+Tenant+Member')",
        "INSERT INTO Permissions VALUES(8, \
                '(01000) Only Admin permissions')",
        "INSERT INTO Permissions VALUES(9, \
                '(01001) Admin+Member')",
        "INSERT INTO Permissions VALUES(10,\
                '(01010) Admin+Tenant')",
        "INSERT INTO Permissions VALUES(11,\
                '(01011) Admin+Tenant+Member')",
        "INSERT INTO Permissions VALUES(12,\
                '(01100) Admin+Manager')",
        "INSERT INTO Permissions VALUES(13,\
                '(01101) Admin+Manager+Member')",
        "INSERT INTO Permissions VALUES(14,\
                '(01110) Admin+Manager+Tenant')",
        "INSERT INTO Permissions VALUES(15,\
                '(01111) Admin+Manager+Tenant+Member')",
        "INSERT INTO Permissions VALUES(16,\
                '(10000) Only Developer permissions')",
        "INSERT INTO Permissions VALUES(17,\
                '(10001) Developer+Member')",
        "INSERT INTO Permissions VALUES(18,\
                '(10010) Developer+Tenant')",
        "INSERT INTO Permissions VALUES(19,\
                '(10011) Developer+Tenant+Member')",
        "INSERT INTO Permissions VALUES(20,\
                '(10100) Developer+Manager')",
        "INSERT INTO Permissions VALUES(21,\
                '(10101) Developer+Manager+Member')",
        "INSERT INTO Permissions VALUES(22,\
                '(10110) Developer+Manager+Tenant')",
        "INSERT INTO Permissions VALUES(23,\
                '(10111) Developer+Manager+Tenant+Member')",
        "INSERT INTO Permissions VALUES(24,\
                '(11000) Developer+Admin')",
        "INSERT INTO Permissions VALUES(25,\
                '(11001) Developer+Admin+Member')",
        "INSERT INTO Permissions VALUES(26,\
                '(11010) Developer+Admin+Tenant')",
        "INSERT INTO Permissions VALUES(27,\
                '(11011) Developer+Admin+Tenant+Member')",
        "INSERT INTO Permissions VALUES(28,\
                '(11100) Developer+Admin+Manager')",
        "INSERT INTO Permissions VALUES(29,\
                '(11101) Developer+Admin+Manager+Member')",
        "INSERT INTO Permissions VALUES(30,\
                '(11110) Developer+Admin+Manager+Tenant')",
        "INSERT INTO Permissions VALUES(31,\
                '(11111) SUPERUSER=Dev.+Admin+Manager+Tenant+Member')")
    for query in queries:
        execute(query, conn)


def fill_tables_demo(file):
    ''' docstring for fill_tables_demo '''
    conn = open(file)
    '''
    demo_queries = (
        "INSERT INTO Firm(FirmAlias, FirmName, EMail, Telephone,\
                            Street_1, Street_2, City, Region, PostalCode)\
            VALUES('sa',\
                'Sabancı University',\
                'mail@sabanciuniv.edu',\
                '0539471',\
                'Universite Caddesi 27',\
                '',\
                'Tuzla',\
                'Istanbul',\
                '34956')",
        "INSERT INTO ParkingLots(LotAlias, FirmAlias, LotName,\
                            PriceMultiplier, Street_1, Street_2,\
                            City, Region, PostalCode)\
            VALUES('FMAN',\
                'sa',\
                'FMAN Lot',\
                1.0,\
                'Strt1',\
                'Strt2',\
                'Cty',\
                'Rgn',\
                'PstCd')",
        "INSERT INTO Floors(FloorNumber, LotAlias)\
            VALUES('001', 'FMAN')",
        "INSERT INTO Floors(FloorNumber, LotAlias)\
            VALUES('001', 'FENS')",
        "INSERT INTO Floors(FloorNumber, LotAlias)\
            VALUES('001', 'FASS')",
        "INSERT INTO RentalAreas(RentalID,FloorNumber,LotAlias)\
            VALUES('R00101', 'Flr_8', 'ltals')",
        "INSERT INTO ChargeSpots(CSpotID,LotAlias,Floornumber)\
            VALUES('C01111', 'Ltals', 'Flr_8')",
        "INSERT INTO ParkingSpots(PSpotID,LotAlias,FloorNumber)\
            VALUES('PSPD', 'Ltals','flr_8')",
        "INSERT INTO ReservedSpots(PSpotID,MShipNum)\
            VALUES('P01100', 'mshpnm')",
        "INSERT INTO RentalAgreement(RentalID, LotAlias, TenandID,\
                                    StartDate, EndDate, Rent, Duration,\
                                    Description)\
            VALUES('R00101',\
                    'ltals',\
                    'T010101',\
                    'strdt',\
                    'endt',\
                    'ftnt',\
                    'drtn',\
                    'dscrptn')",
        "INSERT INTO TenantContacts(TenantID, Name, Telephone, EMail)\
            VALUES('T010101',\
                'nm',\
                'Telephone',\
                'parkmanager@gmail.com')",
        "INSERT INTO ChargingInfo(CSpotID, StartedAt, CPercentage, CPower,\
                                    ChargeAt)\
            VALUES('C01111', 'strdt', 'cprctg', 'cpwr', 'chrgt')",
        "INSERT INTO ParkingInfo(PSpotID, StartedAt)\
         VALUES('P01100',\
                'strdt')",
        "INSERT INTO Users(UserID,UserName,EMail)\
            VALUES('S0001',\
                   'manager',\
                   'parkmanager@gmail.com')",
        "INSERT INTO UsersCreditentials(UserID, Password)\
            VALUES('0001',\
                   '01000')",
        "INSERT INTO Members(MemberID, UserID, MemberName)\
            VALUES('M00011',\
                    'S0001',\
                    'mmbrnm')",
        "INSERT INTO WalletAccounts(WalletID, MemberID)\
            VALUES('W00101',\
                    'M00011')",
        "INSERT INTO CreditCards(CardID, WalletID, HolderName, ValidUntil)\
             VALUES('C01111',\
                    'W00101',\
                    'hldrnm',\
                    'vldntl')",
        "INSERT INTO CardQuartets(CardID,CardQ1,CardQ2,CardQ3,CardQ4)\
            VALUES('C01111',\
                 'HASHEDxNASDKFCHEJSSMASJVIDIdDM+vs',\
                 'HASHEDxNASDKFCHEJSSMASJVIDIasdaSD',\
                 'HASHEDxNASDKFCHEJSSMASJV23zI5DIDn',\
                 '2345')",
        "INSERT INTO Memberships(MShipNum, MemberID, Type, StartDate,\
                                EndDate, Duration, Price)\
            VALUES('mshpnm',\
                    'M0001',\
                    'typ',\
                    '2019-05-15',\
                    '2019-06-20',\
                    35,\
                    100)",
        "INSERT INTO Discounts(VehicleCount, Discounts)\
            VALUES('vhclcnt',\
                   'dscnts')",
        "INSERT INTO ParkingPrices(VehicleType, StartingFee, ExtraFee)\
            VALUES('vhctyp',\
                  'strngf',\
                  'extrf')",
        "INSERT INTO ChargingPrices(VehicleType, ChargingFeeT1,\
                                    ChargingFeeT2, IdleFee)\
            VALUES('vhctyp',\
                   'chrgf1',\
                   'chrgf2',\
                   'ıdlfe')",
        "INSERT INTO ChargerTiers(ProfileNumber, Tier, VehicleType,\
                                    LowerBound, UpperBound)\
            VALUES('prflnmbr',\
                    'tie',\
                    'vhctyp',\
                    'lwrbnd',\
                    'uprboud')")
    '''
    demo_queries = (
        # Columns of table 'Firm'
        # FirmAlias, FirmName, URL, EMail, Telephone, Street_1, Street_2,
        # City, Region, PostalCode
        "INSERT INTO Firm VALUES(\
            'sa',\
            'Sabancı University',\
            'sabanciuniv.edu',\
            'info@sabanciuniv.edu',\
            '+90 216 483 90 00',\
            'Universite Caddesi 27',\
            '',\
            'Tuzla',\
            'Istanbul',\
            '34956')",
        "INSERT INTO Firm VALUES(\
            'PBG',\
            'Parkhaus-Betriebsgesellschaft m.b.H.',\
            'parkhausfrankfurt.de',\
            'info@parkhausfrankfurt.de',\
            '+49 69 5870930',\
            'Tituscorso 2B',\
            '',\
            'Frankfurt am Main',\
            'Hesse',\
            '60439')",
        "INSERT INTO ParkingLots VALUES(\
            'FMAN',\
            'sa',\
            'FMAN Otoparkı',\
            1.0,\
            'Sabancı anayolu',\
            'Universite Cad',\
            'Istanbul',\
            'Tuzla',\
            '34156')",

        "INSERT INTO Floors VALUES(\
            'F_FMAN_01',\
            '1',\
            'FMAN')",
        "INSERT INTO Floors VALUES(\
            'F_FMAN_00',\
            '0',\
            'FMAN')",
        "INSERT INTO Floors VALUES(\
            'F_FMAN_02',\
            '2',\
            'FMAN')",
        "INSERT INTO Floors VALUES(\
            'F_FMAN_03',\
            '3',\
            'FMAN')",
        "INSERT INTO Floors VALUES(\
            'F_FMAN_-01',\
            '-1',\
            'FMAN')",

        "INSERT INTO ParkingLots VALUES(\
            'FENS',\
            'sa',\
            'FENS Otoparkı',\
             1.1,\
            'Sabancı anayolu',\
            'Universite Cad',\
            'Istanbul',\
            'Tuzla',\
            '34156')",

        "INSERT INTO Floors VALUES(\
            'F_FENS_01',\
            '1',\
            'FENS')",
        "INSERT INTO Floors VALUES(\
            'F_FENS_00',\
            '0',\
            'FENS')",
        "INSERT INTO Floors VALUES(\
            'F_FENS_02',\
            '2',\
            'FENS')",
        "INSERT INTO Floors VALUES(\
            'F_FENS_03',\
            '3',\
            'FENS')",
        "INSERT INTO Floors VALUES(\
            'F_FENS_-01',\
            '-1',\
            'FENS')",

        "INSERT INTO RentalAreas VALUES(\
            'R_FENS_-101',\
            '-1',\
            'FENS'\
                    )",

        "INSERT INTO RentalAreas VALUES(\
            'RA_FENS_-102',\
            '-1',\
            'FENS'\
            )",

        "INSERT INTO RentalAgreement VALUES(\
            'RAg_FENS_-101',\
            'FENS',\
            'TCAN',\
            '2019-01-01',\
            '2020-01-01',\
            '2',\
            '365',\
            'Something'\
                    )",

        "INSERT INTO TenantContacts VALUES(\
            'TCAN',\
            'CAN',\
            '05324262729',\
            'cantaskin@gmail.com'\
                    )",

        "INSERT INTO ChargeSpots VALUES(\
            'C_FMAN_0N12',\
            'FMAN',\
            '0'\
            )",

        "INSERT INTO ChargeSpots VALUES(\
            'C_FMAN_0N11',\
            'FMAN',\
            '0'\
            )",

        "INSERT INTO ChargeSpots VALUES(\
            'C_FENS_0A22',\
            'FENS',\
            '0'\
            )",

        "INSERT INTO ChargeSpots VALUES(\
            'C_FENS_0A21',\
            'FENS',\
            '0'\
            )",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A1', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A2', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A3', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A4', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A5', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A6', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A7', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A8', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A9', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A10', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A11', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A12', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A13', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A14', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A15', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A16', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A17', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A18', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A19', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0A20', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B1', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B2', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B3', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B4', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B5', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B6', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B7', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B8', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B9', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B10', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B11', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B12', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B13', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B14', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B15', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B16', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B17', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B18', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B19', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0B20', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W1', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W2', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W3', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W4', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W5', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W6', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W7', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W8', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W9', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0W10', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C1', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C2', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C3', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C4', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C5', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C6', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C7', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C8', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C9', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0C10', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N1', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N2', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N3', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N4', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N5', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N6', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N7', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N8', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N9', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N10', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N11', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0N12', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S1', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S2', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S3', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S4', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S5', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S6', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S7', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S8', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S9', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S10', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S11', 'FENS', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FENS_0S12', 'FENS', '0')",

        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A1', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A2', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A3', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A4', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A5', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A6', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A7', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A8', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A9', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A10', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A11', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A12', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A13', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0A14', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B1', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B2', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B3', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B4', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B5', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B6', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B7', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B8', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B9', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B10', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B11', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B12', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B13', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0B14', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S1', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S2', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S3', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S4', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S5', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S6', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S7', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S8', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S9', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S10', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S11', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S12', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S13', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0S14', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N1', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N2', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N3', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N4', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N5', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N6', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N7', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N8', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N9', 'FMAN', '0')",
        "INSERT INTO ParkingSpots VALUES('P_FMAN_0N10', 'FMAN', '0')",
        # Add demo users
        # Users:
        #   {
        #   {
        #       email: admin@example.com
        #       password: 123456
        #       role: admin
        #   },
        #   {
        #       email: cormen@gmail.com
        #       password: 123456
        #       role: member
        #   },
        #   {
        #       email: rivest@rivest.com
        #       password: 00000
        #       role: member
        #   }
        # }'''
        # User 1
        "INSERT INTO Users VALUES('U00000001', 'admin', 'admin@example.com')",
        "INSERT INTO UsersCreditentials VALUES('U00000001','$argon2id$v=19$m=102400,t=2,p=8$QkkaiHxSgXCvVPp4VHOUwA$28snrSeIVK9/FfhhP+SyXw')",
        "INSERT INTO UserPermissions VALUES('U00000001', '31')",
        # User 2
        "INSERT INTO Users VALUES('U00000002', 'cormen', 'cormen@gmail.com')",
        "INSERT INTO UsersCreditentials VALUES('U00000002', '$argon2id$v=19$m=102400,t=2,p=8$0kiIbTYtha5X4PczSO8qnw$VuVF2X9hOnqPbIlBRSfWuQ')",
        "INSERT INTO UserPermissions VALUES('U00000002', '1')",
        # User 3
        "INSERT INTO Users VALUES('U00000003', 'rivest', 'rivest@rivest.com')",
        "INSERT INTO UsersCreditentials VALUES('U00000003', '$argon2id$v=19$m=102400,t=2,p=8$4Yr0bg0AxuxrElypDIK6cw$7KepS6bSVpPpNQsFX+wfwg')",
        "INSERT INTO UserPermissions VALUES('U00000003', '1')"
    )
    for query in demo_queries:
        execute(query, conn)
    conn.close()
