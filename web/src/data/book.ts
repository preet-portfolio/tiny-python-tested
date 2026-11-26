/** The book's chapters, the mechanic each one teaches, and the real-world case I test it on. */
export type Chapter = {
  id: string;
  number: number;
  title: string;
  program: string;
  mechanic: string;
  world: string;
};

export const BOOK: Chapter[] = [
  { id: "02_crowsnest", number: 2, title: "Crow's Nest", program: "crowsnest.py", mechanic: "Strings and branching", world: "Choosing a or an in generated copy: an hour, a unicorn, an FBI agent" },
  { id: "03_picnic", number: 3, title: "Picnic", program: "picnic.py", mechanic: "Lists, sorting, joining", world: "Oxford-comma lists in notifications" },
  { id: "04_jump_the_five", number: 4, title: "Jump the Five", program: "jump.py", mechanic: "A dictionary as a cipher", world: "Masking phone numbers in logs" },
  { id: "05_howler", number: 5, title: "Howler", program: "howler.py", mechanic: "Files versus STDIN and STDOUT", world: "One tool that reads a file or a pipe" },
  { id: "06_wc", number: 6, title: "Words Count", program: "wc.py", mechanic: "STDIN and column formatting", world: "Matching Unix wc on UTF-8 text" },
  { id: "07_gashlycrumb", number: 7, title: "Gashlycrumb", program: "gashlycrumb.py", mechanic: "A lookup table read from a file", world: "Lookups with missing and duplicate keys" },
  { id: "08_apples_and_bananas", number: 8, title: "Apples and Bananas", program: "apples.py", mechanic: "Eight refactors, one test suite", world: "Refactoring safely under tests" },
  { id: "09_abuse", number: 9, title: "Dial-a-Curse", program: "abuse.py", mechanic: "Seeded randomness, argument errors", world: "Reproducible fake test data" },
  { id: "10_telephone", number: 10, title: "Telephone", program: "telephone.py", mechanic: "Random mutation by seed", world: "Fuzzing input with seeded noise" },
  { id: "11_bottles_of_beer", number: 11, title: "Bottles of Beer", program: "bottles.py", mechanic: "Test-driving one function", world: "Unit tests next to end-to-end tests" },
  { id: "12_ransom", number: 12, title: "Ransom", program: "ransom.py", mechanic: "A coin flip per character", world: "The same seed in two Pythons" },
  { id: "13_twelve_days", number: 13, title: "Twelve Days", program: "twelve_days.py", mechanic: "Cumulative output, golden files", world: "Snapshot testing" },
  { id: "14_rhymer", number: 14, title: "Rhymer", program: "rhymer.py", mechanic: "Regular expression groups", world: "Name variants from a word stem" },
  { id: "15_kentucky_friar", number: 15, title: "Kentucky Friar", program: "friar.py", mechanic: "Substitution with context", world: "Locale text transforms" },
  { id: "16_scrambler", number: 16, title: "Scrambler", program: "scrambler.py", mechanic: "Shuffling inside words", world: "Can people still read scrambled copy?" },
  { id: "17_mad_libs", number: 17, title: "Mad Libs", program: "mad.py", mechanic: "Templates with regular expressions", world: "Email templates with missing placeholders" },
  { id: "18_gematria", number: 18, title: "Gematria", program: "gematria.py", mechanic: "Character codes and sums", world: "Simple checksums and their collisions" },
  { id: "19_wod", number: 19, title: "Workout of the Day", program: "wod.py", mechanic: "Reading CSV, printing tables", world: "A plan generated from a spreadsheet" },
  { id: "20_password", number: 20, title: "Password", program: "password.py", mechanic: "Sets and sampling", world: "Passphrases and how guessable they are" },
  { id: "21_tictactoe", number: 21, title: "Tic-Tac-Toe", program: "tictactoe.py", mechanic: "Validating board state", world: "Trusting state that arrives in a URL" },
  { id: "22_itictactoe", number: 22, title: "Interactive Tic-Tac-Toe", program: "itictactoe.py", mechanic: "Typed state and a game loop", world: "Letting mypy check the state" },
];

export const BOOK_URL = "https://www.manning.com/books/tiny-python-projects";
export const REPO_URL = "https://github.com/kyclark/tiny_python_projects";
