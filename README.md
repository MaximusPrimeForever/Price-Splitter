# Price-Splitter
A small utility written with Python and a Qt-based GUI for splitting prices between multiple people, and summing the share of each person.

## Installing

```powershell
pip install -r requirements
```

## How to run

```powershell
python splitter.py Person1 Person2 ... PersonN
```

Pass the names of all participants as arguments.

## Usage

1. Enter the product price in the top box.
   <img src="README.assets/image-20210909200554046.png" alt="image-20210909200554046" style="zoom:80%;" />
2. Select the participants.
   <img src="README.assets/image-20210909200534948.png" alt="image-20210909200534948" style="zoom:80%;" />

3. Click `Add to total`
   <img src="README.assets/image-20210909200654212.png" alt="image-20210909200654212" style="zoom:80%;" />
   The share of each person should be reflected on the right.
   The total cost is shown at the bottom.

### Deleting an entry

After entering multiple entries suppose you want to delete an entry due to a mistake.

1. Click the dropdown menu on the right.
   <img src="README.assets/image-20210909200916854.png" alt="image-20210909200916854" style="zoom:80%;" />

2. Select the entry.
3. Click `Clear entry`.
4. The next entry will be loaded.

You can select `Current` from the dropdown to show the current state (total price, and shares).
