"""
Train a IncidentClassifier on an excel file.
"""
import argparse
import pandas as pd
from sklearn.externals import joblib
from cvac.model import IncidentClassifier

def main():
    """
    Entry point for train_model.py.
    """
    parser = argparse.ArgumentParser(
        description='Train a new model')

    parser.add_argument('infile', metavar='IF',
                        help='Excel file to train on')
    parser.add_argument('outfile', metavar='OF',
                        help='Output file for classifier (.pkl)')

    parser.add_argument('--sheetname', dest='sheetname',
                        default=0, help='Which sheet to open')
    args = parser.parse_args()

    print('Reading file:', args.infile)
    df = pd.read_excel(args.infile, sheet_name=args.sheetname, header=0)

    print('Training classifier on {} examples...'.format(len(df)))
    classifier = IncidentClassifier()
    classifier.fit(df, df['Type of call'])

    print('Done, writing to file:', args.outfile)
    joblib.dump(classifier, args.outfile)

if __name__ == '__main__':
    main()
