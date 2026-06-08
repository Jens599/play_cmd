from __future__ import annotations

import shutil
import subprocess
from urllib.parse import quote

from play_cmd.models import ResultType, SearchResult

SEARCH_PRINT_TEMPLATE = (
    "%(title)s\t%(id)s\t%(ie_key)s\t%(webpage_url)s\t"
    "%(duration_string)s\t%(uploader)s\t%(view_count)s"
)
PLAYLIST_SEARCH_PARAMETER = "EgIQAw%3D%3D"


class YtdlpNotFoundError(RuntimeError):
    pass


class SearchError(RuntimeError):
    pass


def require_ytdlp() -> str:
    command = shutil.which("yt-dlp")
    if command is None:
        msg = "yt-dlp is missing from PATH. Install yt-dlp for search functionality."
        raise YtdlpNotFoundError(msg)
    return command


def build_search_url(query: str, playlist: bool = False) -> str:
    url = f"https://www.youtube.com/results?search_query={quote(query, safe='')}"
    if playlist:
        url = f"{url}&sp={PLAYLIST_SEARCH_PARAMETER}"
    return url


def build_ytdlp_search_args(
    query: str,
    max_results: int,
    playlist: bool = False,
    cookie_path: str | None = None,
) -> list[str]:
    if max_results < 1 or max_results > 50:
        msg = "max_results must be between 1 and 50"
        raise ValueError(msg)

    args = [
        build_search_url(query, playlist=playlist),
        "--print",
        SEARCH_PRINT_TEMPLATE,
        "--flat-playlist",
        "--playlist-items",
        f"1:{max_results}",
    ]
    if cookie_path:
        args.extend(["--cookies", cookie_path])
    return args


def detect_result_type(id_: str, ie_key: str | None, webpage_url: str | None) -> ResultType:
    url = webpage_url or ""
    if "/playlist?list=" in url or id_.startswith(("PL", "UU")):
        return ResultType.playlist
    if (
        any(marker in url for marker in ("/channel", "/c/", "/user/", "/@"))
        or id_.startswith("UC")
        or ie_key == "YoutubeTab"
    ):
        return ResultType.channel
    return ResultType.video


def parse_search_row(row: str) -> SearchResult | None:
    parts = row.split("\t", 6)
    if len(parts) < 4 or not parts[0] or not parts[1]:
        return None

    title = parts[0]
    id_ = parts[1]
    ie_key = parts[2] if len(parts) >= 3 else None
    webpage_url = parts[3]
    duration = parts[4] if len(parts) >= 5 and parts[4] != "NA" else None
    uploader = parts[5] if len(parts) >= 6 and parts[5] != "NA" else None
    view_count = parts[6] if len(parts) >= 7 and parts[6] != "NA" else None
    result_type = detect_result_type(id_, ie_key, webpage_url)

    metadata = [value for value in (duration, uploader) if value]
    if view_count:
        try:
            metadata.append(f"{int(view_count):,} views")
        except ValueError:
            metadata.append(f"{view_count} views")

    menu_title = f"[{result_type.value}] {title}"
    if metadata:
        menu_title = f"{menu_title} | {' | '.join(metadata)}"

    return SearchResult(
        title=title,
        id=id_,
        type=result_type,
        url=webpage_url,
        duration=duration,
        uploader=uploader,
        view_count=view_count,
        menu_title=menu_title,
    )


def search_youtube(
    query: str,
    max_results: int,
    playlist: bool = False,
    cookie_path: str | None = None,
    result_type: ResultType | None = None,
) -> list[SearchResult]:
    ytdlp = require_ytdlp()
    args = build_ytdlp_search_args(
        query,
        max_results=max_results,
        playlist=playlist,
        cookie_path=cookie_path,
    )
    completed = subprocess.run(
        [ytdlp, *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"yt-dlp exited with code {completed.returncode}"
        raise SearchError(detail)

    results: list[SearchResult] = []
    for row in completed.stdout.splitlines():
        result = parse_search_row(row)
        if result is None:
            continue
        if result_type and result.type is not result_type:
            continue
        results.append(result)
    return results
