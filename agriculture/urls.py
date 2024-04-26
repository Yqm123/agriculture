"""
URL configuration for agriculture project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import getJsonData, question_answering
from . import getNodesNum
from . import getALabels
from . import getDataByLabel
from . import FormReaction
from . import relation_view
from . import getAnswer
from . import completion
urlpatterns = [
    path("search_relation/", relation_view.search_relation),
    path("getJsonData/", getJsonData.get),
    path("getNodesNum/", getNodesNum.getNodesNum),
    path("getALabels/", getALabels.getALabels),
    path("getDataByLabel/", getDataByLabel.getDataByLabel),
    path("getOtherNodes/", getDataByLabel.getOtherNodes),
    path("create/", FormReaction.create),
    path("deleteNode/", FormReaction.deleteNode),
    path("deleteRel/", FormReaction.deleteRel),
    path("deleteGraph/", FormReaction.deleteGraph),
    path("getRelationNum/", getNodesNum.getRelationNum),
    path("qa/", question_answering.question_answering),
    path("get/", getAnswer.get),
    path("completion/", completion.completion),
]
