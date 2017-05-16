# this will count the votes for Mu Alpha Theta elections as per the constitution

# this uses ranked-choice voting, also known as instant-runoff voting, with
# ties broken using approval votes, with ties in that broken using an RNG

# approval votes are yes/no votes on each candidate - whether the voter would
# be okay with the candidate being elected

# after that, for each position, the voter ranks the candidates from best to
# worst

# if no candidate has a majority - "50% + 1" - the last place candidate is
# eliminated and the votes are redistributed based on what that candidate's
# voters' second choices were
# this keeps going until one candidate has a majority

# if there's more than 1 last-place candidate, the one with the most approval
# votes advances and the others are eliminated

# if, in this scenario, there's a tie in approval votes, one candidate among
# those is chosen to go on using a true random number generated at random.org

# this import is to access random.org in the event of an RNG tie
from urllib.request import urlopen

def vote_counter_display():
    """This is what the user will see. It displays instructions and prompts
    the user for the filename."""

    print("This will count the votes for the Mu Alpha Theta elections.")
    print("It may not work if any two candidates' names are identical.")
    print("In such an event, the votes should be hand-counted.")
    input("Press 'Enter' to begin.")
    print("What is the full filepath to the vote file?")
    filename = input("Make sure the file is a .tsv format. ")
    vote_counter(filename)
    input("Press 'Enter' to close this window.")

def vote_counter(filename):
    """This "shell" function calls the other functions in order and neatly
    contains the entire back end."""

    # creates list of votes
    votes = file_reader(filename)

    # counts approval votes for each candidate
    approval = approval_vote_counter(votes)

    # displays the rounds of voting for each race
    race_number = {0:"President", 1:"Vice president", 2:"Secretary",
    3:"Treasurer"}
    i = 0
    while i < 4:
        print("\n")
        print(race_number[i] + ":")
        first_choice_vote_counter(votes, approval, i, 1)
        i += 1

def file_reader(filename):
    """The following reads in the file, determines the number of candidates
    running, and turns each vote roughly into a list containing four strings
    containing the candidates approved by that voter, followed by four lists of
    that voter's ranked choices; one for each position. It returns that list."""

    infile = open(filename, "r")

    # since the vote file is never large, it's okay to use readlines()
    votes = infile.readlines()
    infile.close()

    # the following determines the number of each candidate running
    num_candidates = votes[0][:-1].split("\t")[5:]
    pres = 0
    vp = 0
    sec = 0
    tr = 0
    for s in num_candidates:
        if "Vice President" in s:
            vp += 1
        elif "President" in s:
            pres += 1
        elif "Secretary" in s:
            sec += 1
        elif "Treasurer" in s:
            tr += 1

    # the following "beautifies" the votes

    # removes header
    votes = votes[1:]

    votes[len(votes)-1] += "\n"

    i = 0
    while i < len(votes):

        # for each vote, creates the list (this is why it's important for it
        # to be a .tsv file)
        # [:-1] cuts off "\n"
        # [1:] cuts off the timestamp
        votes[i] = votes[i][:-1].split("\t")[1:]

        # for each of the 4 races
        # takes each cell for the number of candidates, and puts the cell's
        # contents in a temporary list, then deletes the cell
        # it deletes the cell so the next cell will be in the same position,
        # so the same code can be rerun and the new value will be appended to
        # the temp list

        # this temp list is the ranked list of the voter's choices, and it is
        # appended to the end of the list describing that individual vote

        # that way, when the process is repeated for each successive race, the
        # voter's choices for each race will be appended to the end as a list,
        # eventually leaving the list describing the vote taking the shape
        # described in the docstring
        d = {0:pres, 1:vp, 2:sec, 3:tr}
        j = 0
        while j < 4:

            array = []
            k = 0
            while k < d[j]:
                array.append(votes[i][4])
                del votes[i][4]
                k += 1
            votes[i].append(array)
            j += 1
        i += 1

    return votes

def approval_vote_counter(votes):
    """This function takes in the list of votes and tallies approval votes for
    each candidate."""

    approval = {}

    # for each vote
    for v in votes:

        # for each race
        k = 0
        while k < 4:

            # for each candidate in v, adds 1 to their approval in the approval
            # dict if they already exist as a key; otherwise, adds them as a key
            # with the 1 approval vote they earned so far
            a = v[k].split(", ")
            for i in a:
                try:
                    approval[i] += 1
                except:
                    approval[i] = 1
            k += 1

    return approval

def first_choice_vote_counter(votes, approval, race, round_number):
    """This takes in the list of votes, the approval vote tally, which race
    is being counted (president, etc.), and which round is being counted (which
    means how many times a candidate did not reach a majority and votes had to
    be redistributed."""

    # the following initializes the vote-counting array
    first_choice = [{}, {}, {}, {}]
    for v in votes:
        try:
            first_choice[0][v[4][0]] += 1
        except:
            first_choice[0][v[4][0]] = 1
        try:
            first_choice[1][v[5][0]] += 1
        except:
            first_choice[1][v[5][0]] = 1
        try:
            first_choice[2][v[6][0]] += 1
        except:
            first_choice[2][v[6][0]] = 1
        try:
            first_choice[3][v[7][0]] += 1
        except:
            first_choice[3][v[7][0]] = 1

    # the following determines the number of votes necessary to win
    # and displays that number
    try:
        race_votes = sum(first_choice[race].values()) - first_choice[race][""]
    except:
        race_votes = sum(first_choice[race].values())
    race_votes -= race_votes%2
    votes_to_win = race_votes//2 + 1

    # the following displays the votes for each candidate in each race and
    # checks for a winner
    # it also displays information about the race and the round number of the
    # vote-counting
    print("Count " + str(round_number) + " - " + str(votes_to_win) + \
        " vote(s) needed to win")
    for i in first_choice[race].keys():
        if i != "":
            print(i + ": " + str(first_choice[race][i]) + " vote(s)")
    win, var = check_win(votes, first_choice[race], approval, votes_to_win)
    if win:
        print(var + " wins")
    else:
        return first_choice_vote_counter(var, approval, race, round_number + 1)

def check_win(votes, race, approval, votes_to_win):
    """This takes in the vote list, the race being counted, the approval tally,
    and the number of votes needed to win. If there's a winner, it returns the
    True and the winner; otherwise, it returns False and the vote list to allow
    the calling function to recurse."""

    # the following checks for a winner
    for i in race.keys():
        if i != "" and race[i] >= votes_to_win:
            return True, i

    # the following determines the candidates with the fewest votes
    try:
        del race[""]
    except:
        pass
    fewest = [k for k, v in race.items() if v == min(race.values())]
    if len(fewest) > 1:
        fewest = resolve_tie(fewest, approval)

    # the following redistributes votes
    i = 0
    while i < len(votes):
        j = 4
        while j < 8:
            for c in fewest:
                if c in votes[i][j]:
                    del votes[i][j][votes[i][j].index(c)]
            j += 1
        i += 1
    return False, votes

def resolve_tie(fewest, approval):
    """This simply takes the list "fewest" and the approval tally and checks
    which candidate in "fewest" has the most approval votes."""
    print("Tie resolution between the following candidates:")
    print(", ".join(fewest))

    fewestd = {}
    for c in fewest:
        try:
            print(c + ": " + str(approval[c]) + " approval vote(s)")
            fewestd[c] = approval[c]
        except:
            print(c + ": 0 approval vote(s)")
            fewestd[c] = 0

    most = [k for k, v in fewestd.items() if v == max(fewestd.values())]
    if len(most) > 1:
        most = random_resolve_tie(most)
    else:
        most = most[0]
    print(most + " wins the tie.")

    del fewest[fewest.index(most)]
    return fewest

def random_resolve_tie(most):
    """The following generates a true random number automatically to break the
    tie between the candidates in "most", which is a list."""

    print("A tie among " + str(len(most)) + \
        " candidates will be broken using a true random number generator.")

    # this alphabetizes the list by last name, as specified in the constitution
    most.sort(key=lambda s: s.split()[1])

    for r, c in enumerate(most):
        print(str(r + 1) + " will correspond to " + c + ".")
    print("\n")
    print("********************************************************")
    print("*                                                      *")
    print("*   THE RANDOM NUMBER SHOULD ONLY BE GENERATED ONCE.   *")
    print("*                                                      *")
    print("********************************************************")
    print("\n")
    input("Press 'Enter' to generate a random number to break the tie.")

    with urlopen("https://www.random.org/integers/?num=1&min=1&max=" + \
        str(len(most)) + "&col=1&base=10&format=plain&rnd=new") as infile:
        rand = int(infile.readline())

    print("The random number chosen by the true random number generator at " + \
        "random.org was " + str(rand) + ".")
    print("Thus, " + most[rand-1] + " wins the tie.")
    input("Press 'Enter' to continue the counting of the votes.")
    return most[rand-1]

if __name__ == "__main__":
    vote_counter_display()