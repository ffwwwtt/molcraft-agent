"""Auth router — register, login, refresh."""

import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import get_db
from server.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from server.auth import (
    create_access_token, create_refresh_token, decode_token,
    verify_password, get_user_by_email, create_user, get_user_by_id,
)
from server.models.workspace import Workspace

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ── Email validation ──

# Common disposable / temporary email domains
_DISPOSABLE_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', '10minutemail.com', 'tempmail.com',
    'temp-mail.org', 'throwaway.email', 'sharklasers.com', 'yopmail.com',
    'trashmail.com', 'dispostable.com', 'maildrop.cc', 'getairmail.com',
    'tempinbox.com', 'moakt.com', 'emailondeck.com', 'spamgourmet.com',
    'incognitomail.com', 'anonaddy.com', 'simplelogin.com', '33mail.com',
    '0wnd.net', '0wnd.org', '10minutemail.org', '20minutemail.com',
    '2prong.com', '30minutemail.com', '3d-painting.com', '4warding.com',
    '4warding.net', '4warding.org', '60minutemail.com', '6url.com',
    '75hosting.com', '7tags.com', '9ox.net', 'a-bc.net', 'afrobacon.com',
    'ajaxapp.net', 'amiri.net', 'amiriindustries.com', 'anonbox.net',
    'antichef.com', 'antichef.net', 'baxomale.ht.cx', 'beefmilk.com',
    'binkmail.com', 'bio-muesli.info', 'bobmail.info', 'bodhi.lawlita.com',
    'bofthew.com', 'brefmail.com', 'bsnow.net', 'bugmenever.com',
    'bund.us', 'buro-holding.com', 'casualdx.com', 'chammy.info',
    'chewiemail.com', 'cock.li', 'cool-your.pw', 'courrieltemporaire.com',
    'cuvox.de', 'dacoolest.com', 'dandikmail.com', 'dayrep.com',
    'deadaddress.com', 'deadspam.com', 'despam.it', 'devnullmail.com',
    'dfgh.net', 'digitalsanctuary.com', 'discard.email', 'discardmail.com',
    'discardmail.de', 'disposable-email.ml', 'disposableaddress.com',
    'disposableemailaddresses.com', 'disposableinbox.com', 'dispose.it',
    'disposeamail.com', 'disposemail.com', 'dmarc.ro', 'dodgeit.com',
    'dodgit.com', 'donemail.ru', 'dontreg.com', 'dontsendmespam.de',
    'dump-email.info', 'dumpandjunk.com', 'e4ward.com', 'email60.com',
    'emailinfive.com', 'emailtemporanea.com', 'emailtemporar.ro',
    'emailtemporario.com.br', 'emailthe.net', 'emailtray.com', 'etranquil.com',
    'etranquil.net', 'etranquil.org', 'fakeinbox.com', 'fastacura.com',
    'fastchevy.com', 'fastchrysler.com', 'fastkawasaki.com', 'fastmazda.com',
    'fastmitsubishi.com', 'fastnissan.com', 'fastsubaru.com', 'fastsuzuki.com',
    'fasttoyota.com', 'fastyamaha.com', 'filzmail.com', 'fivemail.de',
    'fleckens.info', 'frapmail.com', 'friendlymail.co.uk', 'front14.org',
    'fuckingduh.com', 'fudgerub.com', 'fyii.de', 'galaxy.tv',
    'garliclife.com', 'get1mail.com', 'get2mail.fr', 'getonemail.com',
    'ghosttexter.de', 'girlsundertheinfluence.com', 'gishpuppy.com',
    'gowikibooks.com', 'gowikicampus.com', 'gowikicars.com',
    'gowikifilms.com', 'gowikigames.com', 'gowikimusic.com',
    'gowikinetwork.com', 'gowikitravel.com', 'gowikitv.com',
    'grandmamail.com', 'great-host.in', 'greensloth.com', 'grr.la',
    'gsrv.co.uk', 'guerrillamail.biz', 'guerrillamail.com',
    'guerrillamail.de', 'guerrillamail.net', 'guerrillamail.org',
    'guerrillamailblock.com', 'gustr.com', 'h.mintemail.com', 'h8s.org',
    'haltospam.com', 'harakirimail.com', 'hartbot.de', 'hidemail.de',
    'hmamail.com', 'hochsitze.com', 'hotpop.com', 'hulapla.de',
    'ieatspam.eu', 'ieatspam.info', 'ihateyou.com', 'imails.info',
    'inbax.tk', 'inboxalias.com', 'inboxclean.com', 'inboxclean.org',
    'inboxdesign.me', 'inboxproxy.com', 'incognitomail.com',
    'insorg-mail.info', 'instant-mail.de', 'ip6.li', 'irish2me.com',
    'iwi.net', 'jil.kofteciyiz.net', 'jetable.com', 'jetable.fr.nf',
    'jetable.net', 'jetable.org', 'jnxjn.com', 'jourrapide.com',
    'jsrsolutions.com', 'kasmail.com', 'kaspop.com', 'keepmymail.com',
    'killmail.com', 'killmail.net', 'kismail.ru', 'klassmaster.com',
    'klassmaster.net', 'klzlk.com', 'kook.ml', 'koszmail.pl',
    'kulturbetrieb.info', 'kurzepost.de', 'l33r.eu', 'lackmail.net',
    'lawlita.com', 'lazyinbox.com', 'letthemeatspam.com', 'lifebyfood.com',
    'link2mail.net', 'litedrop.com', 'lol.ovpn.to', 'lolfreak.net',
    'lookugly.com', 'lopl.co.cc', 'lovefall.ml', 'lr7.us', 'lr78.com',
    'lroid.com', 'm4ilweb.de', 'maboard.com', 'mail-temporaire.fr',
    'mail.by', 'mail.mezimages.net', 'mail.zp.ua', 'mail114.net',
    'mail1a.de', 'mail21.cc', 'mail2rss.org', 'mail333.com', 'mail4trash.com',
    'mailbidon.com', 'mailbiz.biz', 'mailblocks.com', 'mailbox52.ga',
    'mailbucket.org', 'mailcatch.com', 'mailde.de', 'mailde.info',
    'maildrop.cc', 'maildx.com', 'maileater.com', 'mailexpire.com',
    'mailfa.tk', 'mailforspam.com', 'mailfreeonline.com', 'mailfs.com',
    'mailguard.me', 'mailhazard.com', 'mailhazard.us', 'mailimate.com',
    'mailin8r.com', 'mailinater.com', 'mailinator.com', 'mailinator.net',
    'mailinator.org', 'mailinator.us', 'mailinator2.com', 'mailincubator.com',
    'mailismagic.com', 'mailjunk.com', 'mailmate.com', 'mailmoat.com',
    'mailms.com', 'mailnator.com', 'mailnesia.com', 'mailnull.com',
    'mailonaut.com', 'mailorc.com', 'mailorg.org', 'mailox.fun',
    'mailpick.biz', 'mailproxsy.com', 'mailquack.com', 'mailrock.biz',
    'mailscrap.com', 'mailseal.de', 'mailshell.com', 'mailsiphon.com',
    'mailslapping.com', 'mailslite.com', 'mailtemp.fr', 'mailtome.de',
    'mailtothis.com', 'mailtrash.net', 'mailtv.net', 'mailtv.tv',
    'mailzi.ru', 'mailzilla.com', 'mailzilla.org', 'makemetheking.com',
    'manifestgenerator.com', 'manybrain.com', 'mbx.cc', 'mega.zik.dj',
    'meinspamschutz.de', 'meltmail.com', 'messagebeamer.de', 'mezimages.net',
    'mintemail.com', 'misterpinball.de', 'mjukglass.nu', 'moakt.com',
    'mohmal.com', 'moncourrier.fr.nf', 'monemail.fr.nf', 'monmail.fr.nf',
    'monumentmail.com', 'msa.minsmail.com', 'mt2009.com', 'mt2014.com',
    'mx0.wwwnew.eu', 'my10minutemail.com', 'mycard.net.ua', 'mycleaninbox.net',
    'mymail-in.net', 'mypacks.net', 'mypartyclip.de', 'myphantomemail.com',
    'mysamp.de', 'myspaceinc.com', 'myspaceinc.net', 'myspaceinc.org',
    'myspamless.com', 'mytemp.email', 'mytempemail.com', 'mytempmail.com',
    'n2snoop.com', 'n8.gs', 'nepwk.com', 'nervmich.net', 'nervtmich.net',
    'netmails.com', 'netmails.net', 'netzidiot.de', 'neverbox.com',
    'nice-4u.com', 'nincsmail.com', 'nincsmail.hu', 'nnh.com',
    'no-spam.ws', 'noblepioneer.com', 'nomail.pw', 'nomail2me.com',
    'nomorespamemails.com', 'nonspam.eu', 'nonspammer.de', 'noref.in',
    'nospam.ze.tc', 'nospam4.us', 'nospamfor.us', 'nospamthanks.info',
    'notmailinator.com', 'notsharingmy.info', 'nowmymail.com', 'nurfuerspam.de',
    'nus.edu.au', 'nwldx.com', 'objectmail.com', 'obxpestcontrol.com',
    'odaymail.com', 'oneoffemail.com', 'onewaymail.com', 'online.ms',
    'oopi.org', 'opayq.com', 'ordinaryamerican.net', 'otherinbox.com',
    'ourklips.com', 'outlawspam.com', 'ovpn.to', 'owlpic.com',
    'pancakemail.com', 'pimpedup.de', 'pjjkp.com', 'plexolan.de',
    'politikerclub.de', 'pooae.com', 'pookmail.com', 'privacy.net',
    'proxymail.eu', 'prtnx.com', 'punkass.com', 'put2.net',
    'putthisinyourspamdatabase.com', 'pwrby.com', 'qisdo.com', 'qisoa.com',
    'quickinbox.com', 'rcpt.at', 'reallymymail.com', 'realtyalerts.ca',
    'recode.me', 'recursor.net', 'regbypass.com', 'regbypass.comsafe-mail.net',
    'rejectmail.com', 'rklips.com', 'rmqkr.net', 'royal.net',
    'rppkn.com', 'rtrtr.com', 's0ny.net', 'safe-mail.net', 'safetymail.info',
    'safetypost.de', 'sandelf.de', 'saynotospams.com', 'selfdestructingmail.com',
    'sendspamhere.com', 'sharklasers.com', 'shiftmail.com', 'shitmail.org',
    'shitware.nl', 'shortmail.net', 'sibmail.com', 'skeefmail.com',
    'slaskpost.se', 'slipry.net', 'smellfear.com', 'snakemail.com',
    'sneakemail.com', 'sneakmail.de', 'snkmail.com', 'sofimail.com',
    'sofortmail.de', 'softpls.asia', 'solvemail.info', 'spam.la',
    'spam.su', 'spamavert.com', 'spambob.com', 'spambob.net',
    'spambob.org', 'spambog.com', 'spambog.de', 'spambog.net',
    'spambog.ru', 'spambox.info', 'spambox.irishspringrealty.com',
    'spambox.me', 'spambox.org', 'spambox.us', 'spamcannon.com',
    'spamcannon.net', 'spamcero.com', 'spamcon.org', 'spamcorptastic.com',
    'spamcowboy.com', 'spamcowboy.net', 'spamcowboy.org', 'spamday.com',
    'spamdecoy.net', 'spamex.com', 'spamfighter.cf', 'spamfighter.ga',
    'spamfighter.gq', 'spamfighter.ml', 'spamfighter.tk', 'spamfree.eu',
    'spamfree24.com', 'spamfree24.de', 'spamfree24.eu', 'spamfree24.info',
    'spamfree24.net', 'spamfree24.org', 'spamgoes.in', 'spamgourmet.com',
    'spamgourmet.net', 'spamgourmet.org', 'spamherelots.com',
    'spamhole.com', 'spamify.com', 'spaminator.de', 'spamkill.info',
    'spaml.com', 'spaml.de', 'spammotel.com', 'spamobox.com',
    'spamoff.de', 'spamsalad.in', 'spamslicer.com', 'spamspot.com',
    'spamstack.com', 'spamthis.co.uk', 'spamthisplease.com', 'spamtrail.com',
    'spamtrap.ro', 'spamtroll.net', 'spamwc.cf', 'spamwc.ga',
    'spamwc.gq', 'spamwc.ml', 'speed.1s.fr', 'spikio.com',
    'spoofmail.de', 'spybox.de', 'squizzy.de', 'ssoia.com',
    'startkeys.com', 'stexsy.com', 'stinkefinger.net', 'stopmyjunkmail.com',
    'streetwisemail.com', 'stuffmail.de', 'super-auswahl.de', 'supergreatmail.com',
    'supermailer.jp', 'superrito.com', 'surebox.info', 'svk.jp',
    'sweetxxx.de', 't.odmail.cn', 'tafmail.com', 'talkinator.com',
    'tapchicuoihoi.com', 'teewars.org', 'teleworm.com', 'teleworm.us',
    'temp-mail.org', 'temp-mail.ru', 'temp.emeraldwebmail.com',
    'temp15qm.com', 'temp1email.com', 'temp2.email', 'tempail.com',
    'tempemail.biz', 'tempemail.co.za', 'tempemail.com', 'tempemail.net',
    'tempinbox.co.uk', 'tempinbox.com', 'tempmail.eu', 'tempmail.it',
    'tempmail2.com', 'tempmaildemo.com', 'tempmailer.com', 'tempmailer.de',
    'tempomail.fr', 'temporarily.de', 'temporarioemail.com.br',
    'temporaryemail.net', 'temporaryemail.us', 'temporaryinbox.com',
    'temporarymailaddress.com', 'tempsky.com', 'tempthe.net',
    'tempymail.com', 'thanksnospam.info', 'thankyou2010.com',
    'thc.st', 'thecloudindex.com', 'thisisnotmyrealemail.com',
    'thismail.net', 'throwaway.email', 'throwawayemailaddress.com',
    'tilien.com', 'titaspaharpur.com', 'tittbit.in', 'tizi.com',
    'toiea.com', 'toomail.biz', 'topranklist.de', 'tradermail.info',
    'trash-amil.com', 'trash-mail.at', 'trash-mail.com', 'trash-mail.de',
    'trash2009.com', 'trashemail.de', 'trashmail.at', 'trashmail.com',
    'trashmail.de', 'trashmail.me', 'trashmail.net', 'trashmail.org',
    'trashmail.ws', 'trashmailer.com', 'trashymail.com', 'trashymail.net',
    'trbvm.com', 'trialmail.de', 'trickmail.net', 'trillianpro.com',
    'tryalert.com', 'turual.com', 'tvchd.com', 'twoweirdtricks.com',
    'tyldd.com', 'uggsrock.com', 'umail.net', 'uroid.com',
    'us.af', 'victime.ninja', 'vickaentb.com', 'vidchart.com',
    'viral-science.fans', 'vistomail.com', 'vomoto.com', 'vp.ycare.de',
    'vpn.st', 'vsimcard.com', 'vssms.com', 'wasteland.rfc822.org',
    'webcontact-france.eu', 'webm4il.info', 'weg-werf-email.de',
    'wegwerf-email-addressen.de', 'wegwerf-email.net', 'wegwerf-email.org',
    'wegwerf-emails.de', 'wegwerfadresse.de', 'wegwerfmail.com',
    'wegwerfmail.de', 'wegwerfmail.info', 'wegwerfmail.net', 'wegwerfmail.org',
    'wetrainbayarea.com', 'wetrainbayarea.org', 'wh4f.org', 'whyspam.me',
    'wilemail.com', 'willhackforfood.biz', 'willselfdestruct.com',
    'winemaven.info', 'wronghead.com', 'wuzup.net', 'wuzupmail.net',
    'www.e4ward.com', 'www.gishpuppy.com', 'www.mailinator.com',
    'wwwnew.eu', 'x.ip6.li', 'xcode.ro', 'xemaps.com',
    'xents.com', 'xmaily.com', 'xoxy.net', 'xyzfree.net',
    'yapped.net', 'yeah.net.bro', 'yep.it', 'yogamaven.com',
    'yopmail.com', 'yopmail.fr', 'yopmail.net', 'yopmail.org',
    'yourdomain.com.pro', 'ypmail.webarnak.fr.eu.org', 'yuurok.com',
    'z1p.biz', 'za.com.ro', 'zehnminuten.de', 'zehnminutenmail.de',
    'zippymail.info', 'zoaxe.com', 'zoemail.com', 'zoemail.net',
    'zoemail.org',
}

# Email regex — balanced production pattern
_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

# Domain part must end with a valid TLD (at least one dot, last segment letters only)
_DOMAIN_RE = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$')


def _validate_email(email: str) -> str | None:
    """Return error message if email is invalid, None if valid."""
    # 1. Trim and lowercase domain
    email = email.strip().lower()

    # 2. Basic length checks (RFC 5321)
    if len(email) > 254:
        return "邮箱地址过长，最多254个字符"
    if '..' in email:
        return "邮箱格式不正确，不能包含连续的点"

    local, _, domain = email.partition('@')

    if not local or not domain:
        return "邮箱格式不正确，缺少@符号或域名"

    if len(local) > 64:
        return "邮箱前缀过长，最多64个字符"

    # 3. Regex format check
    if not _EMAIL_RE.match(email):
        return "邮箱格式不正确，请输入有效的邮箱地址"

    # 4. Domain structure check
    if not _DOMAIN_RE.match(domain):
        return "邮箱域名格式不正确"

    # 5. Local part rules
    if len(local) < 3:
        return "邮箱前缀太短，至少需要3个字符"
    if local.startswith('.') or local.endswith('.'):
        return "邮箱前缀不能以点号开头或结尾"

    # 6. Common typo detection
    if '@' in local:
        return "邮箱格式不正确，@符号位置错误"
    if not domain or '.' not in domain:
        return "邮箱域名格式不正确，缺少顶级域名"

    # 7. Check domain against known disposable providers
    if domain in _DISPOSABLE_DOMAINS:
        return "不支持使用一次性邮箱注册，请使用常用邮箱"

    # 8. Common provider typo detection
    common_typos = {
        'gmial.com': 'gmail.com', 'gmail.co': 'gmail.com',
        'gmai.com': 'gmail.com', 'gmal.com': 'gmail.com',
        'hotmai.com': 'hotmail.com', 'hotmal.com': 'hotmail.com',
        'outlook.co': 'outlook.com', 'outlok.com': 'outlook.com',
        'yahooo.com': 'yahoo.com', 'yaho.com': 'yahoo.com',
        'qq.con': 'qq.com', 'qq.co': 'qq.com',
        '163.con': '163.com', '163.co': '163.com',
    }
    if domain in common_typos:
        return f"邮箱域名可能拼写错误，您是否想输入 @{common_typos[domain]}？"

    return None


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user. Returns JWT tokens and auto-creates a workspace."""
    # Check existing first — so already-registered users see the right error
    existing = await get_user_by_email(db, body.email.strip().lower())
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                          detail="该邮箱已被注册，请直接登录或使用其他邮箱")

    # Then validate format for new registrations
    err = _validate_email(body.email)
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    user = await create_user(db, body.email, body.password, body.display_name)

    # Auto-create default workspace
    workspace = Workspace(user_id=user.id, name="My Workspace")
    db.add(workspace)
    await db.commit()

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Get a new access token using a refresh token."""
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = await get_user_by_id(db, payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )


@router.get("/me")
async def me(
    db: AsyncSession = Depends(get_db),
):
    """Placeholder — will show current user info after auth refactor."""
    return {"message": "Auth endpoint placeholder"}
