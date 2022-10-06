from datetime import datetime, timezone, timedelta
import time

'''
Система сама может продиагностировать своё состояние, например, задачей по расписанию, и в результате записать
событие с этим уровнем. Это могут быть проверки подключаемых ресурсов или что - то конкретное, например, баланс
на счету используемого внешнего ресурса.
'''
EVENT_ALERT = 1

'''
Событие, когда сбой даёт компонент системы, который очень важен и всегда должен работать. Это уже сильно зависит
от того, чем занимается система. Подходит для событий, о которых важно оперативно узнать, даже если оно произошло
всего раз.
'''
EVENT_CRITICAL = 2

'''
Событие о, котором при скором повторении нужно сообщить. Не удалось выполнить действие, которое обязательно
должно быть выполнено, но при этом такое действие не попадает под описание critical. Например, не удалось сохранить
аватарку пользователя по его запросу, но при этом система не является сервисом аватарок, а является чат - системой.
'''
EVENT_ERROR = 4

'''
События, для немедленного уведомления о которых нужно набрать значительное их количество за период времени. Не удалось
выполнить действие, невыполнение которого ничего серьезного не ломает. Это всё ещё ошибки, но исправление которых
может ждать рабочего расписания. Например, не удалось сохранить аватарку пользователя, а система — интернет - магазин.
Уведомление о них нужно (при высокой частоте), чтобы узнать о внезапных аномалиях, потому что они могут быть симптомами
более серьезных проблем.
'''
EVENT_WARNING = 8

'''
События, которые сообщают о предусмотренных системой отклонениях, которые являются частью нормального 
функционирования системы. Например, пользователь указал неправильный пароль при входе, пользователь не заполнил
отчество, но оно и не обязательно, пользователь купил заказ за 0 рублей, но у вас такое предусмотрено в редких
случаях. Уведомление по ним при высокой частоте тоже нужно, так как резкий рост числа отклонений может быть
результатом допущенной ошибки, которую срочно нужно исправить.
'''
EVENT_NOTICE = 16

'''
События, возникновение которых сообщает о нормальном функционировании системы. Например, пользователь зарегистрировался, 
пользователь приобрел товар, пользователь оставил отзыв. Уведомление по таким событиями нужно настраивать в обратном
виде: если за период времени произошло недостаточное количество таких событий, то нужно уведомить, потому что их
снижение могло быть вызвано в результате допущенной ошибки.
'''
EVENT_INFO = 32

'''
События для отладки какого - либо процесса в системе. При добавлении достаточного количества данных в контекст события 
можно произвести диагностику проблемы, либо заключить об исправном функционировании процесса в системе.Например, 
пользователь открыл страницу с товаром и получил список рекомендаций.Значительно увеличивает количество отправляемых 
событий, поэтому допустимо убирать логирование таких событий через некоторое время.Как результат, количество таких 
событий в нормальном функционировании будет переменным, тогда и мониторинг для уведомления по ним можно не подключать.
'''
EVENT_DEBUG = 64

'''
Событие исключение. Нужно проигнорировать.Создается в том случае, если в настройках указано исключать(игнорировать) 
исходное событие.
'''
EVENT_EXCLUDE = 8192

_eventDataList = {
    EVENT_ALERT: {'name': 'ALERT', 'alert': True},
    EVENT_CRITICAL: {'name': 'CRITICAL', 'alert': True},
    EVENT_ERROR: {'name': 'ERROR', 'alert': True},
    EVENT_WARNING: {'name': 'WARNING', 'alert': True},
    EVENT_NOTICE: {'name': 'NOTICE', 'alert': False},
    EVENT_INFO: {'name': 'INFO', 'alert': False},
    EVENT_DEBUG: {'name': 'DEBUG', 'alert': False},
    EVENT_EXCLUDE: {'name': 'EXCLUDE', 'alert': False}
}

_eventNameToLevel = {
    'ALERT': EVENT_ALERT,
    'CRITICAL': EVENT_CRITICAL,
    'ERROR': EVENT_ERROR,
    'WARNING': EVENT_WARNING,
    'NOTICE': EVENT_NOTICE,
    'INFO': EVENT_INFO,
    'DEBUG': EVENT_DEBUG,
    'EXCLUDE': EVENT_EXCLUDE
}

_formatDefault = '{datatimeiso} - {levelname} - {message}'


def _get_datatime_iso() -> str:
    dst = int(time.altzone / 3600) * -1
    tz = timezone(timedelta(hours=dst))
    now = datetime.now(tz)
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + str(tz)[3:]
    # return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + now.strftime('%z')


class MyLoggerClass:
    def __init__(self,
                 file: str,
                 format_line: str = _formatDefault,
                 format_data: dict = None,
                 stdout=None,
                 stderr=None):
        self.file = file
        self.format_data = {} if format_data is None else format_data

        self.stdout = open('/dev/null', 'a+') if stdout is None else stdout
        self.stderr = open('/dev/null', 'a+') if stderr is None else stderr

        # test format
        try:
            format_line.format(**(self.__format_data()))
            self.format_line = format_line
        except KeyError:
            self.format_line = _formatDefault

    def alert(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_ALERT, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_CRITICAL, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_ERROR, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_WARNING, msg, *args, **kwargs)

    def notice(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_NOTICE, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_INFO, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_DEBUG, msg, *args, **kwargs)

    def exclude(self, msg: str, *args, **kwargs) -> None:
        self.__emit(EVENT_EXCLUDE, msg, *args, **kwargs)

    def __format_data(self,
                      datatimeiso: str = '',
                      levelname: str = '',
                      msg: str = '') -> dict:
        list_data = {
            'datatimeiso': datatimeiso,
            'levelname': levelname,
            'message': msg
        }
        return dict(list(self.format_data.items()) + list(list_data.items()))

    def __emit(self, level: int, msg: str, *args, **kwargs) -> None:
        file = open(self.file, 'a')
        log_string = self.format_line.format(**(self.__format_data(
            datatimeiso=_get_datatime_iso(),
            levelname=_eventDataList[level]['name'],
            msg=msg))) + "\n"

        if len(args):
            log_string += 'Context args: ' + str(args) + "\n"

        if len(kwargs):
            log_string += 'Context kwargs: ' + str(kwargs) + "\n"

        file.write(log_string)
        (self.stdout if 1 else self.stderr).write(log_string)
        file.close()
