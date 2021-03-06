import datetime
import pandas as pd

from finance.science import predictor
from finance.science.utilities import science_utils

SYMBOL = 'symbol'
TARGET = 'target'
DENORMALIZED_TARGET = 'denormalized_target'
PREDICTION = 'prediction'
DENORMALIZED_PREDICTION = 'denormalized_prediction'
NORMALIZATION_MIN = 'normalization_min'
NORMALIZATION_MAX = 'normalization_max'


class StockPredictor(predictor.Predictor):
    """Predict the high stocks prices over the next 30 days"""

    @property
    def model_id(self) -> str:
        return 's0'

    @property
    def query(self) -> str:
        query = f'''
            with
            tickers as (
                select distinct
                      ticker
                    , sector
                    , industry
                from nasdaq.listed_stocks
                where   ticker !~ '[\^.~]'
                    and character_length(ticker) between 1 and 4
                    and ticker in ('KO', 'JPM', 'AA')
                limit 30
                )
            , lagged as (
                select
                      s.symbol
                    , s.market_datetime
                    , max(s.open) over (partition by s.symbol order by s.market_datetime rows between 1 following and 31 following) as target
                    , s.open
                    , lag(s.open,  1) over (partition by s.symbol order by s.market_datetime) as open_1
                    , lag(s.open,  2) over (partition by s.symbol order by s.market_datetime) as open_2
                    , lag(s.open,  3) over (partition by s.symbol order by s.market_datetime) as open_3
                    , lag(s.open,  4) over (partition by s.symbol order by s.market_datetime) as open_4
                    , lag(s.open,  5) over (partition by s.symbol order by s.market_datetime) as open_5
                    , lag(s.open,  6) over (partition by s.symbol order by s.market_datetime) as open_6
                    , lag(s.open,  7) over (partition by s.symbol order by s.market_datetime) as open_7
                    , lag(s.open,  8) over (partition by s.symbol order by s.market_datetime) as open_8
                    , lag(s.open,  9) over (partition by s.symbol order by s.market_datetime) as open_9
                    , lag(s.open, 10) over (partition by s.symbol order by s.market_datetime) as open_10
                    , lag(s.open, 11) over (partition by s.symbol order by s.market_datetime) as open_11
                    , lag(s.open, 12) over (partition by s.symbol order by s.market_datetime) as open_12
                    , lag(s.open, 13) over (partition by s.symbol order by s.market_datetime) as open_13
                    , lag(s.open, 14) over (partition by s.symbol order by s.market_datetime) as open_14
                    , lag(s.open, 15) over (partition by s.symbol order by s.market_datetime) as open_15
                    , lag(s.open, 16) over (partition by s.symbol order by s.market_datetime) as open_16
                    , lag(s.open, 17) over (partition by s.symbol order by s.market_datetime) as open_17
                    , lag(s.open, 18) over (partition by s.symbol order by s.market_datetime) as open_18
                    , lag(s.open, 19) over (partition by s.symbol order by s.market_datetime) as open_19
                    , lag(s.open, 20) over (partition by s.symbol order by s.market_datetime) as open_20
                    , lag(s.open, 21) over (partition by s.symbol order by s.market_datetime) as open_21
                    , lag(s.open, 22) over (partition by s.symbol order by s.market_datetime) as open_22
                    , lag(s.open, 23) over (partition by s.symbol order by s.market_datetime) as open_23
                    , lag(s.open, 24) over (partition by s.symbol order by s.market_datetime) as open_24
                    , lag(s.open, 25) over (partition by s.symbol order by s.market_datetime) as open_25
                    , lag(s.open, 26) over (partition by s.symbol order by s.market_datetime) as open_26
                    , lag(s.open, 27) over (partition by s.symbol order by s.market_datetime) as open_27
                    , lag(s.open, 28) over (partition by s.symbol order by s.market_datetime) as open_28
                    , lag(s.open, 29) over (partition by s.symbol order by s.market_datetime) as open_29
                    , lag(s.open, 30) over (partition by s.symbol order by s.market_datetime) as open_30
                from td.stocks as s
                inner join tickers as t
                    on t.ticker = s.symbol
                where s.market_datetime between '{self.start_date}' and '{self.end_date}'
                )
            , summarized as (
                select *
                    , least(open_1, open_2, open_3, open_4, open_5, open_6, open_7, open_8, open_9, open_10, open_11, open_12, open_13, open_14, open_15, open_16, open_17, open_18, open_19, open_20, open_21, open_22, open_23, open_24, open_25, open_26, open_27, open_28, open_29, open_30) as normalization_min
                    , greatest(open_1, open_2, open_3, open_4, open_5, open_6, open_7, open_8, open_9, open_10, open_11, open_12, open_13, open_14, open_15, open_16, open_17, open_18, open_19, open_20, open_21, open_22, open_23, open_24, open_25, open_26, open_27, open_28, open_29, open_30) as normalization_max
                from lagged
                )
            select
                      symbol
                    , market_datetime
                    , (target - normalization_min) / (normalization_max - normalization_min) as target
                    , target as denormalized_target
                    , normalization_min
                    , normalization_max
                    , (open_1  - normalization_min) / (normalization_max - normalization_min) as open_1
                    , (open_2  - normalization_min) / (normalization_max - normalization_min) as open_2
                    , (open_3  - normalization_min) / (normalization_max - normalization_min) as open_3
                    , (open_4  - normalization_min) / (normalization_max - normalization_min) as open_4
                    , (open_5  - normalization_min) / (normalization_max - normalization_min) as open_5
                    , (open_6  - normalization_min) / (normalization_max - normalization_min) as open_6
                    , (open_7  - normalization_min) / (normalization_max - normalization_min) as open_7
                    , (open_8  - normalization_min) / (normalization_max - normalization_min) as open_8
                    , (open_9  - normalization_min) / (normalization_max - normalization_min) as open_9
                    , (open_10 - normalization_min) / (normalization_max - normalization_min) as open_10
                    , (open_11 - normalization_min) / (normalization_max - normalization_min) as open_11
                    , (open_12 - normalization_min) / (normalization_max - normalization_min) as open_12
                    , (open_13 - normalization_min) / (normalization_max - normalization_min) as open_13
                    , (open_14 - normalization_min) / (normalization_max - normalization_min) as open_14
                    , (open_15 - normalization_min) / (normalization_max - normalization_min) as open_15
                    , (open_16 - normalization_min) / (normalization_max - normalization_min) as open_16
                    , (open_17 - normalization_min) / (normalization_max - normalization_min) as open_17
                    , (open_18 - normalization_min) / (normalization_max - normalization_min) as open_18
                    , (open_19 - normalization_min) / (normalization_max - normalization_min) as open_19
                    , (open_20 - normalization_min) / (normalization_max - normalization_min) as open_20
                    , (open_21 - normalization_min) / (normalization_max - normalization_min) as open_21
                    , (open_22 - normalization_min) / (normalization_max - normalization_min) as open_22
                    , (open_23 - normalization_min) / (normalization_max - normalization_min) as open_23
                    , (open_24 - normalization_min) / (normalization_max - normalization_min) as open_24
                    , (open_25 - normalization_min) / (normalization_max - normalization_min) as open_25
                    , (open_26 - normalization_min) / (normalization_max - normalization_min) as open_26
                    , (open_27 - normalization_min) / (normalization_max - normalization_min) as open_27
                    , (open_28 - normalization_min) / (normalization_max - normalization_min) as open_28
                    , (open_29 - normalization_min) / (normalization_max - normalization_min) as open_29
                    , (open_30 - normalization_min) / (normalization_max - normalization_min) as open_30
            from summarized
            where target is not null and open_30 is not null
            order by market_datetime, symbol
            '''
        return query

    @property
    def target_column(self) -> str:
        return TARGET

    @property
    def columns_to_ignore(self) -> list:
        cols = [
            'market_datetime',
            SYMBOL,
            DENORMALIZED_TARGET,
            NORMALIZATION_MIN,
            NORMALIZATION_MAX,
        ] + [self.target_column]
        return cols

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = science_utils.encode_one_hot(df, [SYMBOL])
        return df

    @property
    def model_args(self) -> dict:
        kwargs = {
            'n_layers': 2,
            'n_training_batches': 1,
            'n_epochs': 250,
            'hidden_shape': 1000,
            'dropout': 0.1,
            'learning_rate': .0001,
            'seed': 44,
        }
        return kwargs

    def postprocess_data(
            self,
            input: pd.DataFrame,
            output: pd.DataFrame,
    ) -> pd.DataFrame:
        output['model_id'] = self.model_id
        df = input[self.columns_to_ignore].join(output)
        df[DENORMALIZED_PREDICTION] = df[PREDICTION] * (df[NORMALIZATION_MAX] - df[NORMALIZATION_MIN]) + df[NORMALIZATION_MIN]
        return df


if __name__ == '__main__':
    StockPredictor().execute()
